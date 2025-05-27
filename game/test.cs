using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class test : MonoBehaviour
{
    public float speed = 5f; // 움직임의 속도를 조절합니다.

    private Rigidbody rb; // Rigidbody 컴포넌트를 저장합니다.

    void Start()
    {
        // 시작할 때 Rigidbody 컴포넌트를 가져옵니다.
        rb = GetComponent<Rigidbody>();
    }

    void Update()
    {
        // 입력을 받습니다.
        float moveHorizontal = Input.GetAxis("Horizontal");

        // 회전력을 계산합니다.
        Vector3 rotation = new Vector3(0.0f, 0.0f, -moveHorizontal) * speed;

        // Rigidbody에 회전력을 추가합니다.
        rb.AddTorque(rotation);
    }
}
