using UnityEngine;

public class TestClickableObject : MonoBehaviour
{
    // 특별한 로직이 필요 없을 수도 있습니다.
    // 플레이어 스CRIPT에서 이미 Raycast로 "test" 태그를 감지하기 때문입니다.
    // 이 스크립트는 해당 오브젝트가 "test" 태그를 가져야 함을 명시적으로 보여줍니다.
    void Start()
    {
        if (!gameObject.CompareTag("test"))
        {
            Debug.LogWarning("이 오브젝트는 'test' 태그를 가져야 플레이어와 상호작용합니다.", gameObject);
        }
    }

    // 필요하다면 클릭 시 추가적인 시각적 효과나 사운드 효과를 넣을 수 있습니다.
    // 예:
    // void OnMouseDown()
    // {
    //     // 클릭 시 반짝이는 효과 등
    //     Debug.Log(gameObject.name + " 클릭됨!");
    // }
}
