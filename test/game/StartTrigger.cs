using UnityEngine;

public class StartTrigger : MonoBehaviour
{
    public Vector3 playerSpawnPosition = new Vector3(2, 37, 0);

    void Start()
    {
        if (!gameObject.CompareTag("start"))
        {
            Debug.LogWarning("이 오브젝트는 'start' 태그를 가져야 합니다.", gameObject);
        }
    }

    // 플레이어 스크립트에서 이미 충돌 로직을 처리하고 있습니다.
    // 이 스크립트는 주로 설정값을 가지고 있거나,
    // 플레이어가 통과했을 때 비활성화되는 등의 로직을 추가할 수 있습니다.
    void OnTriggerEnter2D(Collider2D other)
    {
        if (other.CompareTag("Player"))
        {
            // Player playerScript = other.GetComponent<Player>();
            // if (playerScript != null)
            // {
            //     playerScript.transform.position = playerSpawnPosition;
            //     playerScript.newPlayerPosition = playerSpawnPosition;
            //     Debug.Log("시작 트리거 발동! 플레이어 위치 및 새 플레이어 스폰 위치 변경됨: " + playerSpawnPosition);
            //
            //     // 한번 발동 후 비활성화 또는 파괴
            //     // gameObject.SetActive(false);
            // }
        }
    }
}
