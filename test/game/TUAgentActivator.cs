using UnityEngine;

public class TUAgentActivator : MonoBehaviour
{
    public string targetAiTag = "AI"; // 예: AI, AI_1, AI_2
    public Vector3 positionOnEnter = new Vector3(4, 0, 0);
    public Vector3 positionOnExit = new Vector3(2, 2, -11);

    void Start()
    {
        // 자신의 태그에 따라 targetAiTag, positionOnEnter/Exit를 자동 설정할 수도 있음
        // 예: if (gameObject.CompareTag("TU")) { targetAiTag = "AI"; ... }
        // else if (gameObject.CompareTag("TU_1")) { targetAiTag = "AI_1"; ... }
    }

    // 실제 로직은 Player 스크립트에 있으므로,
    // 이 스크립트는 해당 TU 오브젝트의 설정을 관리하거나
    // Player 스크립트에서 이 컴포넌트의 값을 참조하도록 할 수 있습니다.
    // 예를 들어, Player 스크립트에서:
    // TUAgentActivator activator = collision.gameObject.GetComponent<TUAgentActivator>();
    // if (activator != null) {
    //    MoveAIAgents(activator.targetAiTag, activator.positionOnEnter);
    // }

    // 이 스크립트 자체에서 AI 오브젝트를 직접 찾아서 옮기는 로직을 넣을 수도 있습니다.
    // 하지만 Player 스크립트에서 이미 처리 중이므로 중복될 수 있습니다.
}
