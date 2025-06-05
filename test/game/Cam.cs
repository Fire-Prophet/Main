using System.Collections;
using System.Collections.Generic;
using UnityEngine;



public class Cam : MonoBehaviour
{
    private GameObject[] targets;  // 추적 대상 오브젝트 배열
    private int targetIndex;  // 현재 추적 대상의 인덱스

    public int AA = 0;  // 임시 점수

    void Start()
    {
        targetIndex = 0;  // 초기 추적 대상 인덱스 설정
    }

    void Update()
    {

        // ESC 버튼을 누르면
        if (Input.GetKeyDown(KeyCode.Escape))
        {
            // 카메라를 (-75, 0, -10) 좌표로 이동시킵니다.
            transform.position = new Vector3(-75, 0, -10);
            AA--;
        }

        // AA가 1 이상일 때
        if (AA >= 1)
        {
            // 매 프레임마다 "Player" 태그를 가진 모든 오브젝트를 찾습니다.
            targets = GameObject.FindGameObjectsWithTag("Player");

            // H키가 눌리면 추적 대상을 변경합니다.
            if (Input.GetKeyDown(KeyCode.H))
            {
                targetIndex = (targetIndex + 1) % targets.Length;
            }

            // 카메라를 현재 대상에 맞춰 이동시키되, y 좌표는 주인공 오브젝트보다 4 단위 높게 설정합니다.
            transform.position = new Vector3(targets[targetIndex].transform.position.x, targets[targetIndex].transform.position.y + 4, transform.position.z);
        }

        // AA가 0일 때
        if (AA == 0)
        {
            // 마우스 왼쪽 버튼이 눌렸을 때
            if (Input.GetMouseButtonDown(0))
            {
                Vector2 ray = Camera.main.ScreenToWorldPoint(Input.mousePosition);
                RaycastHit2D hit = Physics2D.Raycast(ray, Vector2.zero);

                // 클릭한 위치에 오브젝트가 있을 때
                if (hit.collider != null)
                {
                    // 그 오브젝트의 태그가 "test"일 때
                    if (hit.collider.gameObject.CompareTag("test"))
                    {
                        targets = GameObject.FindGameObjectsWithTag("Player");
                        AA++;  // AA 값을 1 증가시킵니다.
                    }
                }
            }
        }
    }
}



