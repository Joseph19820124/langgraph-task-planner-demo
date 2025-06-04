"""LangGraph圖構建模塊

本模塊展示了如何使用LangGraph構建完整的狀態圖工作流：
- StateGraph的創建和配置
- 節點的添加和連接
- 條件邊的實現
- 圖的編譯和執行
"""

from typing import Dict, Any, Optional, List
from langgraph.graph import StateGraph, START, END
from langgraph.types import Send

from .state import PlannerState, create_initial_state
from .schemas import PlannerConfig
from .nodes import (
    analyze_goal,
    breakdown_tasks,
    evaluate_tasks,
    create_plan,
    get_feedback,
    refine_plan,
    should_get_feedback,
    should_refine_plan,
    has_errors
)


def create_planner_graph() -> StateGraph:
    """創建任務規劃器圖
    
    這個函數展示了LangGraph的完整使用模式：
    1. 創建StateGraph實例
    2. 添加所有節點
    3. 定義節點間的連接關係
    4. 添加條件邊實現分支邏輯
    5. 編譯圖為可執行實例
    
    Returns:
        編譯後的LangGraph實例
    """
    
    # === 步驟1: 創建StateGraph ===
    # StateGraph是LangGraph的核心類，管理狀態和工作流
    builder = StateGraph(PlannerState)
    
    # === 步驟2: 添加節點 ===
    # 每個節點代表工作流中的一個處理步驟
    
    # 目標分析節點
    builder.add_node(
        "analyze_goal",      # 節點名稱（字符串標識符）
        analyze_goal         # 節點函數
    )
    
    # 任務分解節點
    builder.add_node("breakdown_tasks", breakdown_tasks)
    
    # 任務評估節點
    builder.add_node("evaluate_tasks", evaluate_tasks)
    
    # 計劃創建節點
    builder.add_node("create_plan", create_plan)
    
    # 反饋收集節點
    builder.add_node("get_feedback", get_feedback)
    
    # 計劃優化節點
    builder.add_node("refine_plan", refine_plan)
    
    # 最終化節點（虛擬節點，用於結束流程）
    builder.add_node("finalize", _finalize_plan)
    
    # 錯誤處理節點
    builder.add_node("error_handler", _handle_errors)
    
    # === 步驟3: 定義線性流程 ===
    # 使用add_edge添加確定性的連接
    
    # 設置入口點：工作流從目標分析開始
    builder.add_edge(START, "analyze_goal")
    
    # 目標分析 → 任務分解
    builder.add_edge("analyze_goal", "breakdown_tasks")
    
    # 任務分解 → 任務評估
    builder.add_edge("breakdown_tasks", "evaluate_tasks")
    
    # 任務評估 → 計劃創建
    builder.add_edge("evaluate_tasks", "create_plan")
    
    # === 步驟4: 添加條件邊 ===
    # 條件邊根據狀態內容決定下一步行動
    
    # 計劃創建後的分支邏輯
    builder.add_conditional_edges(
        "create_plan",           # 源節點
        should_get_feedback,     # 條件函數
        {
            "get_feedback": "get_feedback",  # 條件函數返回值 → 目標節點
            "finalize": "finalize"
        }
    )
    
    # 反饋收集後的分支邏輯
    builder.add_conditional_edges(
        "get_feedback",
        should_refine_plan,
        {
            "refine_plan": "refine_plan",
            "finalize": "finalize"
        }
    )
    
    # 計劃優化後的循環邏輯
    builder.add_conditional_edges(
        "refine_plan",
        should_refine_plan,  # 重用條件函數
        {
            "refine_plan": "get_feedback",  # 繼續優化循環
            "finalize": "finalize"           # 結束優化
        }
    )
    
    # === 步驟5: 設置出口點 ===
    # 最終化節點連接到END
    builder.add_edge("finalize", END)
    builder.add_edge("error_handler", END)
    
    # === 步驟6: 編譯圖 ===
    # 編譯將圖轉換為可執行的實例
    graph = builder.compile(
        name="task_planner",           # 圖的名稱
        debug=True                     # 啟用調試模式
    )
    
    return graph


def create_simple_planner_graph() -> StateGraph:
    """創建簡化版的任務規劃器圖
    
    這個函數展示了更簡單的LangGraph使用模式，適合初學者：
    - 線性工作流
    - 最少的條件邏輯
    - 專注於核心功能
    
    Returns:
        編譯後的簡化LangGraph實例
    """
    
    builder = StateGraph(PlannerState)
    
    # 添加核心節點
    builder.add_node("analyze_goal", analyze_goal)
    builder.add_node("breakdown_tasks", breakdown_tasks)
    builder.add_node("evaluate_tasks", evaluate_tasks)
    builder.add_node("create_plan", create_plan)
    builder.add_node("finalize", _finalize_plan)
    
    # 線性連接
    builder.add_edge(START, "analyze_goal")
    builder.add_edge("analyze_goal", "breakdown_tasks")
    builder.add_edge("breakdown_tasks", "evaluate_tasks")
    builder.add_edge("evaluate_tasks", "create_plan")
    builder.add_edge("create_plan", "finalize")
    builder.add_edge("finalize", END)
    
    return builder.compile(name="simple_task_planner")


def create_advanced_planner_graph() -> StateGraph:
    """創建高級版的任務規劃器圖
    
    展示LangGraph的高級特性：
    - 並行處理
    - 複雜條件邏輯
    - 錯誤恢復
    - 狀態監控
    
    Returns:
        編譯後的高級LangGraph實例
    """
    
    builder = StateGraph(PlannerState)
    
    # 添加所有節點
    builder.add_node("analyze_goal", analyze_goal)
    builder.add_node("breakdown_tasks", breakdown_tasks)
    builder.add_node("evaluate_tasks", evaluate_tasks)
    builder.add_node("create_plan", create_plan)
    builder.add_node("get_feedback", get_feedback)
    builder.add_node("refine_plan", refine_plan)
    builder.add_node("finalize", _finalize_plan)
    builder.add_node("error_handler", _handle_errors)
    builder.add_node("state_monitor", _monitor_state)
    
    # 添加並行任務節點
    builder.add_node("parallel_analysis", _parallel_analysis)
    builder.add_node("risk_assessment", _assess_risks)
    builder.add_node("resource_check", _check_resources)
    
    # 主流程
    builder.add_edge(START, "analyze_goal")
    builder.add_edge("analyze_goal", "breakdown_tasks")
    
    # 並行分析分支
    builder.add_conditional_edges(
        "breakdown_tasks",
        _should_do_parallel_analysis,
        {
            "parallel": "parallel_analysis",
            "sequential": "evaluate_tasks"
        }
    )
    
    # 並行任務處理
    builder.add_conditional_edges(
        "parallel_analysis",
        _distribute_parallel_tasks,
        ["risk_assessment", "resource_check"]
    )
    
    # 聚合並行結果
    builder.add_edge("risk_assessment", "evaluate_tasks")
    builder.add_edge("resource_check", "evaluate_tasks")
    
    # 後續流程
    builder.add_edge("evaluate_tasks", "create_plan")
    
    # 複雜的反饋循環
    builder.add_conditional_edges(
        "create_plan",
        _advanced_feedback_logic,
        {
            "auto_approve": "finalize",
            "get_feedback": "get_feedback",
            "need_revision": "refine_plan"
        }
    )
    
    # 高級優化循環
    builder.add_conditional_edges(
        "get_feedback",
        _advanced_refinement_logic,
        {
            "refine": "refine_plan",
            "finalize": "finalize",
            "restart": "breakdown_tasks"  # 重大修改時重新開始
        }
    )
    
    # 狀態監控
    builder.add_edge("refine_plan", "state_monitor")
    builder.add_conditional_edges(
        "state_monitor",
        _check_iteration_limit,
        {
            "continue": "get_feedback",
            "force_finalize": "finalize",
            "error": "error_handler"
        }
    )
    
    # 錯誤處理和恢復
    builder.add_conditional_edges(
        "error_handler",
        _error_recovery_logic,
        {
            "retry": "analyze_goal",
            "partial_recovery": "create_plan",
            "terminate": END
        }
    )
    
    # 結束點
    builder.add_edge("finalize", END)
    
    return builder.compile(name="advanced_task_planner")


# === 輔助節點函數 ===

def _finalize_plan(state: PlannerState) -> Dict[str, Any]:
    """最終化計劃
    
    這個節點展示了如何在LangGraph中實現結束邏輯
    
    Args:
        state: 當前狀態
        
    Returns:
        最終狀態更新
    """
    from .state import update_state_metadata, add_processing_note
    from datetime import datetime
    
    execution_plan = state.get("execution_plan")
    iteration_count = state.get("iteration_count", 0)
    
    final_notes = [
        f"計劃最終化完成",
        f"總共進行了 {iteration_count} 次迭代",
        f"最終計劃包含 {len(state.get('subtasks', []))} 個任務"
    ]
    
    if execution_plan:
        final_notes.append(
            f"預估總時間：{execution_plan.estimated_total_hours:.1f} 小時"
        )
    
    return {
        **update_state_metadata(state, "completed"),
        "processing_notes": state.get("processing_notes", []) + final_notes,
        "is_plan_approved": True
    }


def _handle_errors(state: PlannerState) -> Dict[str, Any]:
    """處理錯誤
    
    展示了LangGraph中錯誤處理的模式
    
    Args:
        state: 包含錯誤信息的狀態
        
    Returns:
        錯誤處理後的狀態更新
    """
    from .state import update_state_metadata
    
    errors = state.get("errors", [])
    error_summary = f"處理了 {len(errors)} 個錯誤"
    
    return {
        **update_state_metadata(state, "error_handled"),
        "processing_notes": state.get("processing_notes", []) + [
            error_summary,
            "錯誤處理完成，流程終止"
        ]
    }


def _monitor_state(state: PlannerState) -> Dict[str, Any]:
    """監控狀態
    
    展示了狀態監控和循環控制的模式
    
    Args:
        state: 當前狀態
        
    Returns:
        監控結果的狀態更新
    """
    from .state import update_state_metadata, add_processing_note
    
    iteration_count = state.get("iteration_count", 0)
    config = state.get("config") or PlannerConfig()
    
    monitoring_notes = [
        f"狀態監控：第 {iteration_count} 次迭代",
        f"最大允許迭代：{config.max_iterations}"
    ]
    
    if iteration_count >= config.max_iterations:
        monitoring_notes.append("達到最大迭代次數，準備強制結束")
    
    return {
        **update_state_metadata(state, "monitored"),
        "processing_notes": state.get("processing_notes", []) + monitoring_notes
    }


# === 高級節點函數 ===

def _parallel_analysis(state: PlannerState) -> Dict[str, Any]:
    """並行分析
    
    展示了LangGraph中並行處理的實現模式
    """
    from .state import add_processing_note
    
    subtasks = state.get("subtasks", [])
    
    # 準備並行分析
    parallel_note = f"準備對 {len(subtasks)} 個任務進行並行分析"
    
    return {
        **add_processing_note(state, parallel_note),
        "current_phase": "parallel_analysis"
    }


def _assess_risks(state: PlannerState) -> Dict[str, Any]:
    """風險評估"""
    from .state import add_processing_note
    
    risks = ["時間風險", "技能風險", "資源風險"]
    
    return {
        **add_processing_note(state, f"完成風險評估，識別 {len(risks)} 類風險"),
        "identified_risks": risks
    }


def _check_resources(state: PlannerState) -> Dict[str, Any]:
    """資源檢查"""
    from .state import add_processing_note
    
    resources = ["時間資源", "學習資源", "工具資源"]
    
    return {
        **add_processing_note(state, f"完成資源檢查，評估 {len(resources)} 類資源"),
        "available_resources": resources
    }


# === 高級條件函數 ===

def _should_do_parallel_analysis(state: PlannerState) -> str:
    """決定是否進行並行分析"""
    subtasks = state.get("subtasks", [])
    
    # 如果任務數量較多，使用並行分析
    if len(subtasks) > 5:
        return "parallel"
    else:
        return "sequential"


def _distribute_parallel_tasks(state: PlannerState) -> List[Send]:
    """分發並行任務"""
    return [
        Send("risk_assessment", {"task_type": "risk"}),
        Send("resource_check", {"task_type": "resource"})
    ]


def _advanced_feedback_logic(state: PlannerState) -> str:
    """高級反饋邏輯"""
    config = state.get("config") or PlannerConfig()
    task_analysis = state.get("task_analysis")
    
    # 自動批准簡單計劃
    if (config.auto_approve_simple_plans and 
        task_analysis and 
        task_analysis.complexity_score < 5.0):
        return "auto_approve"
    
    # 複雜計劃需要修改
    if task_analysis and task_analysis.complexity_score > 8.0:
        return "need_revision"
    
    # 普通計劃獲取反饋
    return "get_feedback"


def _advanced_refinement_logic(state: PlannerState) -> str:
    """高級改進邏輯"""
    feedback = state.get("feedback")
    iteration_count = state.get("iteration_count", 0)
    
    if not feedback:
        return "finalize"
    
    # 重大修改需要重新開始
    if "重新設計" in feedback.comments or feedback.rating < 2:
        return "restart"
    
    # 批准的計劃
    if feedback.approval_status:
        return "finalize"
    
    # 需要小幅調整
    return "refine"


def _check_iteration_limit(state: PlannerState) -> str:
    """檢查迭代限制"""
    iteration_count = state.get("iteration_count", 0)
    config = state.get("config") or PlannerConfig()
    errors = state.get("errors", [])
    
    if errors:
        return "error"
    elif iteration_count >= config.max_iterations:
        return "force_finalize"
    else:
        return "continue"


def _error_recovery_logic(state: PlannerState) -> str:
    """錯誤恢復邏輯"""
    errors = state.get("errors", [])
    iteration_count = state.get("iteration_count", 0)
    
    # 如果錯誤不多且還有重試機會
    if len(errors) < 3 and iteration_count < 2:
        return "retry"
    
    # 部分恢復
    execution_plan = state.get("execution_plan")
    if execution_plan:
        return "partial_recovery"
    
    # 終止
    return "terminate"


# === 圖執行輔助函數 ===

def run_planner(user_goal: str, config: Optional[PlannerConfig] = None) -> Dict[str, Any]:
    """運行任務規劃器
    
    這個函數展示了如何執行LangGraph圖
    
    Args:
        user_goal: 用戶目標
        config: 可選的配置
        
    Returns:
        執行結果
    """
    # 創建圖
    graph = create_planner_graph()
    
    # 創建初始狀態
    initial_state = create_initial_state(user_goal, config)
    
    # 執行圖
    result = graph.invoke(initial_state)
    
    return result


def run_simple_planner(user_goal: str) -> Dict[str, Any]:
    """運行簡化版規劃器"""
    graph = create_simple_planner_graph()
    initial_state = create_initial_state(user_goal)
    return graph.invoke(initial_state)


def run_advanced_planner(user_goal: str, config: PlannerConfig) -> Dict[str, Any]:
    """運行高級版規劃器"""
    graph = create_advanced_planner_graph()
    initial_state = create_initial_state(user_goal, config)
    return graph.invoke(initial_state)


# === 調試和監控函數 ===

def visualize_graph(graph_type: str = "standard") -> str:
    """可視化圖結構
    
    Args:
        graph_type: 圖類型 ("standard", "simple", "advanced")
        
    Returns:
        圖的文本表示
    """
    if graph_type == "simple":
        graph = create_simple_planner_graph()
    elif graph_type == "advanced":
        graph = create_advanced_planner_graph()
    else:
        graph = create_planner_graph()
    
    # 返回圖的結構描述（簡化版）
    return f"""
LangGraph 結構 ({graph_type}):
- 節點數量: {len(graph.nodes)}
- 邊數量: {len(graph.edges)}
- 入口點: START
- 出口點: END
- 支持並行: {'是' if graph_type == 'advanced' else '否'}
- 錯誤處理: {'完整' if graph_type in ['standard', 'advanced'] else '基本'}
"""


def get_execution_trace(result: Dict[str, Any]) -> List[str]:
    """獲取執行軌跡
    
    Args:
        result: 圖執行結果
        
    Returns:
        執行步驟列表
    """
    notes = result.get("processing_notes", [])
    phases = []
    
    current_phase = result.get("current_phase", "unknown")
    phases.append(f"最終階段: {current_phase}")
    
    for note in notes:
        phases.append(f"- {note}")
    
    return phases
