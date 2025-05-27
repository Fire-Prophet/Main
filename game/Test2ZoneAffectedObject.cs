using UnityEngine;

[RequireComponent(typeof(Rigidbody2D), typeof(SpriteRenderer))]
public class Test2ZoneAffectedObject : MonoBehaviour
{
    private Rigidbody2D rb;
    private SpriteRenderer sr;
    private Color originalColor;
    private float originalGravityScale;
    private bool originalIsKinematic;

    void Start()
    {
        if (!gameObject.CompareTag("test_2"))
        {
            Debug.LogWarning("이 오브젝트는 'test_2' 태그를 가져야 플레이어의 구역 감지에 반응합니다.", gameObject);
            // 태그가 없으면 스크립트 비활성화 또는 파괴도 고려 가능
            // this.enabled = false;
            // Destroy(this);
            return;
        }

        rb = GetComponent<Rigidbody2D>();
        sr = GetComponent<SpriteRenderer>();
        originalColor = sr.color;
        originalGravityScale = rb.gravityScale;
        originalIsKinematic = rb.isKinematic;
    }

    // 플레이어 스크립트에서 직접 이 오브젝트의 속성을 변경하므로,
    // 이 스크립트에서는 원래 상태로 돌아가는 로직을 추가할 수 있습니다.
    // 예를 들어, 플레이어가 구역을 벗어났을 때 호출될 함수
    public void RestoreOriginalState()
    {
        if (sr != null) sr.color = originalColor;
        if (rb != null)
        {
            rb.gravityScale = originalGravityScale;
            rb.isKinematic = originalIsKinematic;
        }
        Debug.Log(gameObject.name + "의 상태가 원래대로 복원되었습니다.");
    }

    // 플레이어 스크립트에서 변경하는 부분을 여기로 옮겨 관리할 수도 있습니다.
    public void ApplyZoneEffect()
    {
        if (rb != null)
        {
            rb.isKinematic = false;
            rb.gravityScale = 10;
        }
        if (sr != null)
        {
            Color c = sr.color;
            c.a = 0.5f;
            sr.color = c;
        }
        Debug.Log(gameObject.name + "에 구역 효과가 적용되었습니다.");
    }
}
