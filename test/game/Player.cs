using System.Collections;
using System.Collections.Generic;
using UnityEngine;


public class Player : MonoBehaviour
{
    public float speed = 10.0f; // 플레이어의 이동 속도
    public float jumpForce = 5.0f; // 플레이어의 점프 힘
    public int point = 3; // 플레이어의 포인트

    private float moveInput; // 플레이어의 이동 입력
    private bool isGrounded = false; // 플레이어가 땅에 있는지 여부
    private float originalGravity; // 원래의 중력 값
    private float timeInAir = 0.0f; // 공중에 머무는 시간
    private bool isFixed = false; // 플레이어가 고정되었는지 여부

    private Rigidbody2D rb; // 플레이어의 리지드바디
    private List<GameObject> fixedObjects = new List<GameObject>(); // 고정된 오브젝트들의 리스트


    public bool canMove = false;  // 플레이어가 움직일 수 있는지 여부를 결정하는 변수

    

    public Vector3 newPlayerPosition = new Vector3(0, 0, 0); // 새 플레이어의 위치

    void Start() // 시작할 때
    {
        rb = GetComponent<Rigidbody2D>(); // 리지드바디 컴포넌트를 가져옴
        originalGravity = rb.gravityScale; // 원래의 중력 값을 저장


    }

    void Update() // 매 업데이트마다
    {

        Vector3 min = new Vector3(27, 36, 0); // 구역의 최소 좌표를 설정하세요.
        Vector3 max = new Vector3(28, 41, 0); // 구역의 최대 좌표를 설정하세요.

        if (transform.position.x >= min.x && transform.position.x <= max.x &&
        transform.position.y >= min.y && transform.position.y <= max.y)
        {
            GameObject[] objects = GameObject.FindGameObjectsWithTag("test_2");
            foreach (GameObject obj in objects)
            {
                Rigidbody2D rb = obj.GetComponent<Rigidbody2D>();
                rb.isKinematic = false;
                rb.gravityScale = 10;

                SpriteRenderer sr = obj.GetComponent<SpriteRenderer>();
                Color c = sr.color;
                c.a = 0.5f; // 투명도를 0.5로 설정하세요.
                sr.color = c;
            }
        }




        // "test" 태그가 할당된 오브젝트를 클릭하면 플레이어의 움직임을 활성화합니다.
        if (Input.GetMouseButtonDown(0))
        {
            Vector2 ray = Camera.main.ScreenToWorldPoint(Input.mousePosition);
            RaycastHit2D hit = Physics2D.Raycast(ray, Vector2.zero);

            if (hit.collider != null)
            {
                if (hit.collider.gameObject.CompareTag("test"))
                {
                    canMove = true;
                }
            }
        }

        // 플레이어의 움직임이 활성화되면 원하는 조작을 수행합니다.
        if (canMove)
        {
            if (!isFixed) // 플레이어가 고정되지 않았다면
            {
                MovePlayer(); // 플레이어 이동
                JumpPlayer(); // 플레이어 점프
            }

            if (point >= 1 && Input.GetKeyDown(KeyCode.H)) // 포인트가 1 이상이고 H키를 눌렀다면
            {
                HandlePlayerFixation(); // 플레이어 고정 처리
            }

            if (Input.GetKeyDown(KeyCode.G)) // G키를 눌렀다면
            {
                ResetPlayer(); // 플레이어 리셋
            }
        }



        // ESC 버튼을 누르면
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            point = 3;
            foreach (GameObject obj in fixedObjects) // 고정된 오브젝트 리스트의 각 오브젝트에 대해
            {
                Destroy(obj); // 오브젝트를 파괴
            }

            transform.position = new Vector3(0, -2, 0);



        }










    }

    void MovePlayer() // 플레이어 이동 함수
    {
        moveInput = Input.GetAxis("Horizontal"); // 수평축 입력을 받음
        rb.velocity = new Vector2(moveInput * speed, rb.velocity.y); // 플레이어의 속도를 설정
    }

    void JumpPlayer() // 플레이어 점프 함수
    {
        if (isGrounded && Input.GetKeyDown(KeyCode.Space)) // 플레이어가 땅에 있고 스페이스바를 눌렀다면
        {
            rb.velocity = Vector2.up * jumpForce; // 플레이어를 위로 점프시킴
        }

        if (!isGrounded) // 플레이어가 공중에 있다면
        {
            timeInAir += Time.deltaTime; // 공중에 머무는 시간을 증가시킴
            rb.gravityScale = originalGravity * Mathf.Pow(2, timeInAir); // 중력을 시간에 따라 증가시킴
        }
        else // 플레이어가 땅에 있다면
        {
            timeInAir = 0.0f; // 공중에 머무는 시간을 초기화
            rb.gravityScale = originalGravity; // 중력을 원래 값으로 복원
        }
    }

    void HandlePlayerFixation() // 플레이어 고정 처리 함수
    {
        point--; // 포인트 감소
        if (!isFixed) // 플레이어가 고정되지 않았다면
        {
            isFixed = true; // 플레이어를 고정
            rb.velocity = Vector2.zero; // 플레이어의 속도를 0으로 설정
            rb.bodyType = RigidbodyType2D.Kinematic; // 플레이어의 바디 타입을 Kinematic으로 설정
            rb.gravityScale = 0; // 플레이어의 중력을 0으로 설정
            gameObject.tag = "Ground"; // 플레이어의 태그를 Ground로 설정
            CreateNewPlayer(); // 새 플레이어 생성
        }
    }

    void CreateNewPlayer() // 새 플레이어 생성 함수
    {
        GameObject newPlayer = Instantiate(gameObject, newPlayerPosition, Quaternion.identity); // 새 플레이어를 생성
        newPlayer.GetComponent<Rigidbody2D>().bodyType = RigidbodyType2D.Dynamic; // 새 플레이어의 바디 타입을 Dynamic으로 설정
        newPlayer.GetComponent<Rigidbody2D>().gravityScale = originalGravity; // 새 플레이어의 중력을 원래 값으로 설정
        newPlayer.tag = "Player"; // 새 플레이어의 태그를 Player로 설정
        fixedObjects.Add(gameObject); // 고정된 오브젝트 리스트에 추가
    }

    void ResetPlayer() // 플레이어 리셋 함수
    {
        point = 3; // 포인트를 3으로 설정
        foreach (GameObject obj in fixedObjects) // 고정된 오브젝트 리스트의 각 오브젝트에 대해
        {
            Destroy(obj); // 오브젝트를 파괴
        }
        fixedObjects.Clear(); // 고정된 오브젝트 리스트를 비움
    }






    void OnCollisionEnter2D(Collision2D collision) // 충돌 감지
    {



        if (collision.gameObject.CompareTag("Ground")) // Ground 태그를 가진 오브젝트와 충돌하면
        {
            isGrounded = true; // 땅에 닿아 있음

        }

        if (collision.gameObject.CompareTag("Box")) // Box 태그를 가진 오브젝트와 충돌하면
        {
            transform.position = new Vector3(0, 0, 0); // (0, 0, 0) 좌표로 이동
        }

        if (collision.gameObject.CompareTag("Box_1")) // Box_1 태그를 가진 오브젝트와 충돌하면
        {
            transform.position = new Vector3(2, 37, 0); // (2, 37, 0) 좌표로 이동
        }



        // 충돌한 오브젝트가 'start' 태그를 가지고 있는지 확인합니다.
        if (collision.gameObject.tag == "start")
        {
            // 주인공의 위치를 (2, 20.56, 0)으로 변경합니다.
            transform.position = new Vector3(2, 37, 0);
            // 새로운 주인공 오브젝트의 생성 위치를 (2, 20.56, 0)으로 변경
            newPlayerPosition = new Vector3(2, 37, 0);
        }




        // 주인공 오브젝트가 TU 태그가 부여된 오브젝트와 충돌했는지 확인
        if (collision.gameObject.tag == "TU")
        {
            // AI 태그가 부여된 모든 오브젝트를 찾아서 이동
            GameObject[] aiObjects = GameObject.FindGameObjectsWithTag("AI");
            foreach (GameObject aiObject in aiObjects)
            {
                aiObject.transform.position = new Vector3(4, 0, 0);
            }
        }


        // 주인공 오브젝트가 TU 태그가 부여된 오브젝트와 충돌했는지 확인
        if (collision.gameObject.tag == "TU_1")
        {
            // AI 태그가 부여된 모든 오브젝트를 찾아서 이동
            GameObject[] aiObjects = GameObject.FindGameObjectsWithTag("AI_1");
            foreach (GameObject aiObject in aiObjects)
            {
                aiObject.transform.position = new Vector3(20, 0, 0);
            }
        }


        // 주인공 오브젝트가 TU 태그가 부여된 오브젝트와 충돌했는지 확인
        if (collision.gameObject.tag == "TU_2")
        {
            // AI 태그가 부여된 모든 오브젝트를 찾아서 이동
            GameObject[] aiObjects = GameObject.FindGameObjectsWithTag("AI_2");
            foreach (GameObject aiObject in aiObjects)
            {
                aiObject.transform.position = new Vector3(50, 0, 0);
            }
        }


    }

    void OnCollisionExit2D(Collision2D collision) // 충돌이 끝나면
    {
        if (collision.gameObject.CompareTag("Ground")) // Ground 태그를 가진 오브젝트와의 충돌이 끝나면
        {
            isGrounded = false; // 땅에 닿아 있지 않음
        }

        if (collision.gameObject.CompareTag("TU")) // TU 태그를 가진 오브젝트와의 충돌이 끝나면
        {
            // AI 태그가 부여된 모든 오브젝트를 찾아서 이동
            GameObject[] aiObjects = GameObject.FindGameObjectsWithTag("AI");
            foreach (GameObject aiObject in aiObjects)
            {
                aiObject.transform.position = new Vector3(2, 2, -11);
            }
        }

        if (collision.gameObject.CompareTag("TU_1")) // TU 태그를 가진 오브젝트와의 충돌이 끝나면
        {
            // AI 태그가 부여된 모든 오브젝트를 찾아서 이동
            GameObject[] aiObjects = GameObject.FindGameObjectsWithTag("AI_1");
            foreach (GameObject aiObject in aiObjects)
            {
                aiObject.transform.position = new Vector3(2, 2, -11);
            }
        }


        if (collision.gameObject.CompareTag("TU_2")) // TU 태그를 가진 오브젝트와의 충돌이 끝나면
        {
            // AI 태그가 부여된 모든 오브젝트를 찾아서 이동
            GameObject[] aiObjects = GameObject.FindGameObjectsWithTag("AI_2");
            foreach (GameObject aiObject in aiObjects)
            {
                aiObject.transform.position = new Vector3(2, 2, -11);
            }
        }




    }
}
