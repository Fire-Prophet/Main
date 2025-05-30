using UnityEngine;

public class HazardBox : MonoBehaviour
{
    public enum ResetType { DefaultOrigin, SpecificPosition }
    public ResetType type = ResetType.DefaultOrigin;
    public Vector3 specificResetPosition = new Vector3(2, 37, 0); // Box_1의 경우

    void Start()
    {
        // 태그에 따라 타입을 미리 설정할 수 있도록 함
        if (gameObject.CompareTag("Box"))
        {
            type = ResetType.DefaultOrigin;
        }
        else if (gameObject.CompareTag("Box_1"))
        {
            type = ResetType.SpecificPosition;
        }
        // "start" 태그에 대한 처리는 Player 스크립트에 이미 있으므로 여기서는 제외
    }

    // Player 스크립트에서 충돌 시 직접 위치를 변경하므로,
    // 이 스크립트는 주로 해당 오브젝트의 역할을 명시하거나,
    // 추가적인 효과(예: 파티클, 사운드)를 줄 때 사용될 수 있습니다.
    void OnCollisionEnter2D(Collision2D collision)
    {
        if (collision.gameObject.CompareTag("Player"))
        {
            // Player 스크립트에서 이미 처리하고 있으므로, 여기서는 로깅 또는 추가 효과만.
            // Player player = collision.gameObject.GetComponent<Player>();
            // if (player != null)
            // {
            //    Vector3 targetPosition = (type == ResetType.DefaultOrigin) ? Vector3.zero : specificResetPosition;
            //    Debug.Log(gameObject.name + "에 의해 플레이어가 " + targetPosition + "으로 이동됩니다.");
            //    // player.transform.position = targetPosition; // Player 스크립트가 하도록 둡니다.
            // }
        }
    }
}
