using UnityEngine;

public class SimpleAI : MonoBehaviour
{
    // 이 AI 오브젝트의 태그는 "AI", "AI_1", "AI_2" 중 하나여야 합니다.
    void Start()
    {
        // 초기 위치 설정이나 기타 AI 로직 (예: 순찰, 플레이어 감지 등)
        // 현재는 Player 스크립트에 의해 위치가 강제로 제어됩니다.
        Debug.Log(gameObject.name + " AI 오브젝트 활성화. 태그: " + gameObject.tag);
    }

    public void MoveToPosition(Vector3 newPosition)
    {
        // 부드러운 이동을 원한다면 Lerp 또는 MoveTowards 사용 가능
        transform.position = newPosition;
        Debug.Log(gameObject.name + "가 " + newPosition + "으로 이동했습니다.");
    }

    // 추가적인 AI 행동
    // void Update()
    // {
    //     // 예: 플레이어 추적, 특정 패턴으로 움직이기 등
    // }
}
