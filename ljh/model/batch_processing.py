"""
Batch Processing and Distributed Computing System for Fire Simulations
Enables parallel execution of multiple simulations across multiple processes/machines.
This script handles batch processing of fire simulations.
"""

import multiprocessing as mp
import concurrent.futures
import queue
import time
import uuid
import pickle
import json
from typing import List, Dict, Any, Optional, Callable, Union
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
from datetime import datetime
import hashlib
import redis
from threading import Thread, Event
import subprocess
import os


@dataclass
class SimulationJob:
    """Represents a single simulation job."""
    job_id: str
    parameters: Dict[str, Any]
    priority: int = 5
    created_at: datetime = None
    status: str = "pending"  # pending, running, completed, failed
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    worker_id: Optional[str] = None
    execution_time: Optional[float] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data['created_at'] = self.created_at.isoformat()
        return data
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SimulationJob':
        """Create from dictionary."""
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)


class JobQueue:
    """Thread-safe job queue with priority support."""
    
    def __init__(self, maxsize: int = 0):
        self.queue = queue.PriorityQueue(maxsize=maxsize)
        self.jobs = {}  # job_id -> SimulationJob
        self._lock = mp.Lock()
    
    def add_job(self, job: SimulationJob) -> None:
        """Add job to queue."""
        with self._lock:
            # Use negative priority for max-heap behavior
            self.queue.put((-job.priority, job.created_at, job.job_id))
            self.jobs[job.job_id] = job
    
    def get_job(self, timeout: Optional[float] = None) -> Optional[SimulationJob]:
        """Get next job from queue."""
        try:
            _, _, job_id = self.queue.get(timeout=timeout)
            with self._lock:
                job = self.jobs.get(job_id)
                if job:
                    job.status = "running"
                return job
        except queue.Empty:
            return None
    
    def update_job(self, job: SimulationJob) -> None:
        """Update job status."""
        with self._lock:
            self.jobs[job.job_id] = job
    
    def get_job_status(self, job_id: str) -> Optional[SimulationJob]:
        """Get job by ID."""
        with self._lock:
            return self.jobs.get(job_id)
    
    def get_all_jobs(self) -> List[SimulationJob]:
        """Get all jobs."""
        with self._lock:
            return list(self.jobs.values())


class DistributedJobQueue:
    """Redis-based distributed job queue."""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_client = redis.from_url(redis_url)
        self.job_queue_key = "fire_sim:jobs:pending"
        self.job_data_key = "fire_sim:jobs:data"
        self.worker_key = "fire_sim:workers"
    
    def add_job(self, job: SimulationJob) -> None:
        """Add job to distributed queue."""
        # Store job data
        self.redis_client.hset(
            self.job_data_key,
            job.job_id,
            json.dumps(job.to_dict())
        )
        
        # Add to priority queue
        self.redis_client.zadd(
            self.job_queue_key,
            {job.job_id: job.priority}
        )

    def get_job(self, worker_id: str) -> Optional[SimulationJob]:
        """Get next job for worker."""
        # Get highest priority job
        job_ids = self.redis_client.zrevrange(self.job_queue_key, 0, 0)
        if not job_ids:
            return None
        
        job_id = job_ids[0].decode()
        
        # Remove from pending queue
        removed = self.redis_client.zrem(self.job_queue_key, job_id)
        if not removed:
            return None  # Job was taken by another worker
        
        # Get job data
        job_data = self.redis_client.hget(self.job_data_key, job_id)
        if not job_data:
            return None
        
        job = SimulationJob.from_dict(json.loads(job_data))
        job.status = "running"
        job.worker_id = worker_id
        
        # Update job data
        self.redis_client.hset(
            self.job_data_key,
            job_id,
            json.dumps(job.to_dict())
        )
        
        # Register worker activity
        self.redis_client.hset(
            self.worker_key,
            worker_id,
            json.dumps({
                "last_seen": datetime.now().isoformat(),
                "current_job": job_id
            })
        )
        
        return job
    
    def update_job(self, job: SimulationJob) -> None:
        """Update job in distributed storage."""
        self.redis_client.hset(
            self.job_data_key,
            job.job_id,
            json.dumps(job.to_dict())
        )


class SimulationWorker:
    """Worker process for executing simulation jobs."""
    
    def __init__(self, worker_id: str, simulation_func: Callable, queue_system: Union[JobQueue, DistributedJobQueue]):
        self.worker_id = worker_id
        self.simulation_func = simulation_func
        self.queue_system = queue_system
        self.logger = logging.getLogger(f"worker.{worker_id}")
        self.running = False
        self.stop_event = Event()
    
    def start(self) -> None:
        """Start worker process."""
        self.running = True
        self.logger.info(f"Worker {self.worker_id} started")
        
        while self.running and not self.stop_event.is_set():
            try:
                job = self.queue_system.get_job(timeout=5.0)
                if job:
                    self._execute_job(job)
                else:
                    time.sleep(1)  # No jobs available
            except Exception as e:
                self.logger.error(f"Worker error: {e}")
                time.sleep(5)
    
    def stop(self) -> None:
        """Stop worker process."""
        self.running = False
        self.stop_event.set()
    
    def _execute_job(self, job: SimulationJob) -> None:
        """Execute a simulation job."""
        start_time = time.time()
        self.logger.info(f"Executing job {job.job_id}")
        
        try:
            # Run simulation
            result = self.simulation_func(**job.parameters)
            
            # Update job with result
            job.status = "completed"
            job.result = result
            job.execution_time = time.time() - start_time
            
            self.logger.info(f"Job {job.job_id} completed in {job.execution_time:.2f}s")
            
        except Exception as e:
            job.status = "failed"
            job.error = str(e)
            job.execution_time = time.time() - start_time
            
            self.logger.error(f"Job {job.job_id} failed: {e}")
        
        # Update job in queue system
        self.queue_system.update_job(job)


class BatchProcessor:
    """Manages batch processing of multiple simulations."""
    
    def __init__(self, num_workers: int = None, use_distributed: bool = False, redis_url: str = None):
        self.num_workers = num_workers or mp.cpu_count()
        self.use_distributed = use_distributed
        
        if use_distributed:
            self.queue_system = DistributedJobQueue(redis_url or "redis://localhost:6379/0")
        else:
            self.queue_system = JobQueue()
        
        self.workers = []
        self.logger = logging.getLogger("batch_processor")
    
    def submit_job(self, parameters: Dict[str, Any], priority: int = 5) -> str:
        """Submit a simulation job."""
        job_id = str(uuid.uuid4())
        job = SimulationJob(
            job_id=job_id,
            parameters=parameters,
            priority=priority
        )
        
        self.queue_system.add_job(job)
        self.logger.info(f"Submitted job {job_id} with priority {priority}")
        
        return job_id
    
    def submit_batch(self, parameter_sets: List[Dict[str, Any]], priority: int = 5) -> List[str]:
        """Submit multiple simulation jobs."""
        job_ids = []
        for params in parameter_sets:
            job_id = self.submit_job(params, priority)
            job_ids.append(job_id)
        
        self.logger.info(f"Submitted batch of {len(job_ids)} jobs")
        return job_ids
    
    def start_workers(self, simulation_func: Callable) -> None:
        """Start worker processes."""
        for i in range(self.num_workers):
            worker_id = f"worker_{i}"
            worker = SimulationWorker(worker_id, simulation_func, self.queue_system)
            
            if self.use_distributed:
                # Start as separate process for distributed mode
                process = mp.Process(target=worker.start)
                process.start()
                self.workers.append(process)
            else:
                # Start as thread for local mode
                thread = Thread(target=worker.start)
                thread.daemon = True
                thread.start()
                self.workers.append(worker)
        
        self.logger.info(f"Started {self.num_workers} workers")
    
    def stop_workers(self) -> None:
        """Stop all workers."""
        for worker in self.workers:
            if hasattr(worker, 'stop'):
                worker.stop()
            elif hasattr(worker, 'terminate'):
                worker.terminate()
        
        self.workers.clear()
        self.logger.info("Stopped all workers")
    
    def get_job_status(self, job_id: str) -> Optional[SimulationJob]:
        """Get status of a job."""
        return self.queue_system.get_job_status(job_id)
    
    def wait_for_completion(self, job_ids: List[str], timeout: Optional[float] = None) -> Dict[str, SimulationJob]:
        """Wait for jobs to complete."""
        start_time = time.time()
        completed_jobs = {}
        
        while len(completed_jobs) < len(job_ids):
            for job_id in job_ids:
                if job_id not in completed_jobs:
                    job = self.get_job_status(job_id)
                    if job and job.status in ["completed", "failed"]:
                        completed_jobs[job_id] = job
            
            if timeout and (time.time() - start_time) > timeout:
                break
            
            time.sleep(1)
        
        return completed_jobs
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        all_jobs = self.queue_system.get_all_jobs()
        
        stats = {
            "total_jobs": len(all_jobs),
            "pending": len([j for j in all_jobs if j.status == "pending"]),
            "running": len([j for j in all_jobs if j.status == "running"]),
            "completed": len([j for j in all_jobs if j.status == "completed"]),
            "failed": len([j for j in all_jobs if j.status == "failed"]),
            "avg_execution_time": 0.0,
            "total_execution_time": 0.0
        }
        
        completed_jobs = [j for j in all_jobs if j.status == "completed" and j.execution_time]
        if completed_jobs:
            stats["avg_execution_time"] = sum(j.execution_time for j in completed_jobs) / len(completed_jobs)
            stats["total_execution_time"] = sum(j.execution_time for j in completed_jobs)
        
        return stats


class ParameterSweep:
    """Generates parameter combinations for simulation sweeps."""
    
    @staticmethod
    def grid_search(parameter_space: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
        """Generate all combinations of parameters (grid search)."""
        import itertools
        
        keys = list(parameter_space.keys())
        values = list(parameter_space.values())
        
        combinations = []
        for value_combination in itertools.product(*values):
            param_set = dict(zip(keys, value_combination))
            combinations.append(param_set)
        
        return combinations
    
    @staticmethod
    def random_search(parameter_space: Dict[str, List[Any]], num_samples: int, seed: int = None) -> List[Dict[str, Any]]:
        """Generate random parameter combinations."""
        import random
        
        if seed:
            random.seed(seed)
        
        combinations = []
        for _ in range(num_samples):
            param_set = {}
            for key, values in parameter_space.items():
                param_set[key] = random.choice(values)
            combinations.append(param_set)
        
        return combinations
    
    @staticmethod
    def latin_hypercube_sampling(parameter_ranges: Dict[str, tuple], num_samples: int, seed: int = None) -> List[Dict[str, Any]]:
        """Generate Latin Hypercube samples for continuous parameters."""
        import numpy as np
        
        if seed:
            np.random.seed(seed)
        
        num_params = len(parameter_ranges)
        samples = np.random.rand(num_samples, num_params)
        
        # Apply Latin Hypercube sampling
        for i in range(num_params):
            samples[:, i] = (np.argsort(samples[:, i]) + np.random.rand(num_samples)) / num_samples
        
        # Scale to parameter ranges
        param_names = list(parameter_ranges.keys())
        combinations = []
        
        for sample in samples:
            param_set = {}
            for i, param_name in enumerate(param_names):
                min_val, max_val = parameter_ranges[param_name]
                param_set[param_name] = min_val + sample[i] * (max_val - min_val)
            combinations.append(param_set)
        
        return combinations


def example_simulation_function(grid_size: int, wind_speed: float, fuel_moisture: float) -> Dict[str, Any]:
    """Example simulation function for testing."""
    # Simulate some work
    time.sleep(0.1)
    
    # Return mock results
    return {
        "burned_area": grid_size * wind_speed * (1 - fuel_moisture),
        "simulation_time": 0.1,
        "max_fire_intensity": wind_speed * 100,
        "containment_time": fuel_moisture * 60
    }


if __name__ == "__main__":
    # Example usage
    processor = BatchProcessor(num_workers=4, use_distributed=False)
    
    # Generate parameter sweep
    parameter_space = {
        "grid_size": [50, 100, 200],
        "wind_speed": [5.0, 10.0, 15.0, 20.0],
        "fuel_moisture": [0.1, 0.2, 0.3, 0.4]
    }
    
    parameter_sets = ParameterSweep.grid_search(parameter_space)
    print(f"Generated {len(parameter_sets)} parameter combinations")
    
    # Submit batch job
    processor.start_workers(example_simulation_function)
    job_ids = processor.submit_batch(parameter_sets[:10])  # First 10 combinations
    
    # Wait for completion
    print("Waiting for jobs to complete...")
    completed_jobs = processor.wait_for_completion(job_ids, timeout=60)
    
    # Print results
    for job_id, job in completed_jobs.items():
        if job.status == "completed":
            print(f"Job {job_id}: Burned area = {job.result['burned_area']:.2f}")
        else:
            print(f"Job {job_id}: Failed - {job.error}")
    
    # Print statistics
    stats = processor.get_statistics()
    print(f"Statistics: {stats}")
    
    processor.stop_workers()
