using UnityEngine;
using UnityEngine.UI; // 기본 UI Text 사용 시
// using TMPro; // TextMeshPro 사용 시

public class PointDisplayUI : MonoBehaviour
{
    public Player playerScript; // 인스펙터에서 플레이어 오브젝트 할당 필요
    public Text pointText; // 인스펙터에서 UI Text 오브젝트 할당 필요
    // public TextMeshProUGUI pointTextMeshPro; // TextMeshPro 사용 시

    void Start()
    {
        if (playerScript == null)
        {
            Debug.LogError("Player 스크립트가 할당되지 않았습니다!");
            // 필요시 자동으로 플레이어 찾기
            // playerScript = FindObjectOfType<Player>();
        }
        if (pointText == null /* && pointTextMeshPro == null */)
        {
            Debug.LogError("포인트를 표시할 UI Text 오브젝트가 할당되지 않았습니다!");
        }
    }

    void Update()
    {
        if (playerScript != null && pointText != null)
        {
            pointText.text = "Points: " + playerScript.point.ToString();
        }
        // else if (playerScript != null && pointTextMeshPro != null)
        // {
        //     pointTextMeshPro.text = "Points: " + playerScript.point.ToString();
        // }
    }
}
