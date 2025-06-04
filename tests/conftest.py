#!/usr/bin/env python3
"""
Pytest配置文件

定義測試夾具、配置和共享工具函數。
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from datetime import datetime
from typing import Dict, Any, List

from src.state import create_initial_state, PlannerState
from src.schemas import (
    PlannerConfig, 
    Task, 
    TaskDifficulty, 
    TaskAnalysis, 
    ExecutionPlan,
    PlanFeedback
)


# === 測試配置 ===

def pytest_configure(config):
    """Pytest配置"""
    # 添加自定義標記
    config.addinivalue_line(
        "markers", "slow: 標記慢速測試"
    )
    config.addinivalue_line(
        "markers", "integration: 標記集成測試"
    )
    config.addinivalue_line(
        "markers", "unit: 標記單元測試"
    )


# === 基本測試夾具 ===

@pytest.fixture
def sample_config():
    """提供示例配置"""
    return PlannerConfig(
        max_iterations=3,
        auto_approve_simple_plans=True,
        complexity_threshold=7.0,
        include_detailed_timeline=True
    )


@pytest.fixture
def sample_goal():
    """提供示例目標"""
    return "學習Python編程並開發一個Web應用"


@pytest.fixture
def initial_state(sample_goal, sample_config):
    """提供初始狀態"""
    return create_initial_state(sample_goal, sample_config)


@pytest.fixture
def sample_analyzed_goal():
    """提供示例分析目標"""
    return {
        "original_goal": "學習Python編程",
        "goal_type": "learning",
        "complexity_level": "medium",
        "estimated_scope": "medium",
        "key_domains": ["技術"],
        "success_criteria": [
            "完成所有計劃的任務",
            "達到預期的知識/技能水平"
        ],
        "potential_challenges": [
            "時間管理和進度控制",
            "學習曲線和技能獲取"
        ]
    }


@pytest.fixture
def sample_tasks():
    """提供示例任務列表"""
    return [
        Task(
            id="task_001",
            title="需求分析和目標設定",
            description="明確學習目標，分析現有基礎",
            difficulty=TaskDifficulty.EASY,
            estimated_hours=3.0,
            skills_required=["分析思維", "目標設定"]
        ),
        Task(
            id="task_002",
            title="基礎知識學習",
            description="學習Python基礎語法和概念",
            difficulty=TaskDifficulty.MEDIUM,
            estimated_hours=40.0,
            skills_required=["編程基礎", "邏輯思維"],
            prerequisites=["task_001"]
        ),
        Task(
            id="task_003",
            title="實戰項目開發",
            description="開發一個完整的Web應用項目",
            difficulty=TaskDifficulty.HARD,
            estimated_hours=60.0,
            skills_required=["Web開發", "項目管理"],
            prerequisites=["task_002"]
        )
    ]


@pytest.fixture
def sample_task_analysis(sample_tasks):
    """提供示例任務分析"""
    return TaskAnalysis(
        total_tasks=len(sample_tasks),
        total_estimated_hours=sum(task.estimated_hours for task in sample_tasks),
        difficulty_distribution={
            TaskDifficulty.EASY: 1,
            TaskDifficulty.MEDIUM: 1,
            TaskDifficulty.HARD: 1
        },
        skill_requirements={
            "分析思維": 1,
            "目標設定": 1,
            "編程基礎": 1,
            "邏輯思維": 1,
            "Web開發": 1,
            "項目管理": 1
        },
        critical_path=["task_002", "task_003"],
        potential_blockers=["task_003"],
        complexity_score=6.5,
        feasibility_score=7.5
    )


@pytest.fixture
def sample_execution_plan():
    """提供示例執行計劃"""
    start_date = datetime(2024, 1, 1, 9, 0)
    end_date = datetime(2024, 3, 1, 18, 0)
    
    return ExecutionPlan(
        plan_id="plan_test_001",
        title="Python學習執行計劃",
        description="包含3個任務的詳細執行計劃",
        estimated_start_date=start_date,
        estimated_end_date=end_date,
        estimated_total_hours=103.0,
        phases=[
            {
                "phase_name": "準備階段",
                "tasks": ["task_001"],
                "estimated_hours": 3.0,
                "description": "包含1個任務"
            },
            {
                "phase_name": "學習階段",
                "tasks": ["task_002"],
                "estimated_hours": 40.0,
                "description": "包含1個任務"
            },
            {
                "phase_name": "實戰階段",
                "tasks": ["task_003"],
                "estimated_hours": 60.0,
                "description": "包含1個任務"
            }
        ],
        daily_schedule={
            "2024-01-01": ["task_001"],
            "2024-01-02": ["task_002"],
            "2024-02-15": ["task_003"]
        },
        risks=[
            "學習曲線可能較陡",
            "實戰項目可能遇到技術難題"
        ],
        recommendations=[
            "建議設置定期檢查點",
            "尋求社區支持和幫助"
        ],
        milestones=[
            {
                "name": "基礎學習完成",
                "date": "2024-02-01",
                "description": "完成Python基礎學習",
                "tasks_completed": ["task_001", "task_002"]
            },
            {
                "name": "項目完成",
                "date": "2024-03-01",
                "description": "完成Web應用開發",
                "tasks_completed": ["task_001", "task_002", "task_003"]
            }
        ]
    )


@pytest.fixture
def sample_feedback_approved():
    """提供批准的反饋"""
    return PlanFeedback(
        feedback_type="approval",
        rating=5,
        comments="計劃很詳細，我很滿意！",
        suggested_changes=[],
        approval_status=True
    )


@pytest.fixture
def sample_feedback_revision():
    """提供需要修改的反饋"""
    return PlanFeedback(
        feedback_type="revision",
        rating=3,
        comments="計劃需要一些調整",
        suggested_changes=[
            "縮短總體時間",
            "簡化複雜任務",
            "添加更多實踐環節"
        ],
        approval_status=False
    )


# === 複雜測試夾具 ===

@pytest.fixture
def complete_state(initial_state, sample_analyzed_goal, sample_tasks, 
                  sample_task_analysis, sample_execution_plan):
    """提供完整的測試狀態"""
    state = initial_state.copy()
    state.update({
        "analyzed_goal": sample_analyzed_goal,
        "subtasks": sample_tasks,
        "task_analysis": sample_task_analysis,
        "execution_plan": sample_execution_plan,
        "current_phase": "plan_creation_complete",
        "processing_notes": [
            "成功分析目標",
            "完成任務分解",
            "完成任務評估",
            "創建執行計劃"
        ]
    })
    return state


@pytest.fixture
def state_with_feedback(complete_state, sample_feedback_revision):
    """提供包含反饋的狀態"""
    state = complete_state.copy()
    state.update({
        "feedback": sample_feedback_revision,
        "feedback_history": [sample_feedback_revision],
        "iteration_count": 1,
        "is_plan_approved": False
    })
    return state


@pytest.fixture
def error_state(initial_state):
    """提供包含錯誤的狀態"""
    state = initial_state.copy()
    state.update({
        "errors": [
            "測試錯誤1",
            "測試錯誤2"
        ],
        "warnings": [
            "測試警告1"
        ],
        "current_phase": "error_occurred"
    })
    return state


# === 測試工具函數 ===

@pytest.fixture
def assert_valid_state():
    """提供狀態驗證函數"""
    def _assert_valid_state(state: Dict[str, Any]):
        """驗證狀態是否有效"""
        required_fields = [
            "user_goal", "subtasks", "task_analysis", "execution_plan",
            "feedback", "iteration_count", "is_plan_approved",
            "current_phase", "processing_notes", "errors", "session_id"
        ]
        
        for field in required_fields:
            assert field in state, f"缺少必要字段: {field}"
        
        # 類型檢查
        assert isinstance(state["user_goal"], str)
        assert isinstance(state["subtasks"], list)
        assert isinstance(state["iteration_count"], int)
        assert isinstance(state["is_plan_approved"], bool)
        assert isinstance(state["processing_notes"], list)
        assert isinstance(state["errors"], list)
        
        # 業務邏輯檢查
        assert state["iteration_count"] >= 0
        assert state["session_id"] is not None
    
    return _assert_valid_state


@pytest.fixture
def assert_valid_task():
    """提供任務驗證函數"""
    def _assert_valid_task(task: Task):
        """驗證任務是否有效"""
        assert task.id is not None
        assert task.title is not None
        assert task.description is not None
        assert task.estimated_hours > 0
        assert isinstance(task.skills_required, list)
        assert isinstance(task.prerequisites, list)
        assert task.difficulty in TaskDifficulty
    
    return _assert_valid_task


@pytest.fixture
def assert_valid_execution_plan():
    """提供執行計劃驗證函數"""
    def _assert_valid_execution_plan(plan: ExecutionPlan):
        """驗證執行計劃是否有效"""
        assert plan.plan_id is not None
        assert plan.title is not None
        assert plan.description is not None
        assert plan.estimated_total_hours > 0
        assert plan.estimated_start_date < plan.estimated_end_date
        assert isinstance(plan.phases, list)
        assert isinstance(plan.daily_schedule, dict)
        assert isinstance(plan.risks, list)
        assert isinstance(plan.recommendations, list)
        assert isinstance(plan.milestones, list)
        assert plan.version >= 1
    
    return _assert_valid_execution_plan


# === 性能測試夾具 ===

@pytest.fixture
def performance_goals():
    """提供性能測試目標"""
    return [
        "學習基礎編程",
        "開發移動應用",
        "掌握數據科學",
        "提升設計能力",
        "建立個人品牌"
    ]


@pytest.fixture
def benchmark_config():
    """提供基準測試配置"""
    return PlannerConfig(
        max_iterations=1,  # 減少迭代以加快測試
        auto_approve_simple_plans=True,
        complexity_threshold=10.0,  # 高閾值以避免複雜處理
        include_detailed_timeline=False  # 簡化以提高速度
    )


# === 模擬夾具 ===

@pytest.fixture
def mock_llm_response():
    """模擬LLM響應"""
    return {
        "content": "這是一個模擬的LLM響應",
        "usage": {
            "prompt_tokens": 100,
            "completion_tokens": 50,
            "total_tokens": 150
        }
    }


# === 清理夾具 ===

@pytest.fixture(autouse=True)
def cleanup_test_data():
    """自動清理測試數據"""
    # 測試前設置
    yield
    
    # 測試後清理
    import gc
    gc.collect()


# === 跳過條件 ===

def pytest_collection_modifyitems(config, items):
    """修改測試收集"""
    # 如果沒有安裝某些依賴，跳過相關測試
    try:
        import psutil
    except ImportError:
        skip_performance = pytest.mark.skip(reason="需要psutil進行性能測試")
        for item in items:
            if "performance" in item.nodeid:
                item.add_marker(skip_performance)
    
    # 標記慢速測試
    for item in items:
        if "benchmark" in item.nodeid or "integration" in item.nodeid:
            item.add_marker(pytest.mark.slow)


# === 自定義標記 ===

pytestmark = [
    pytest.mark.unit,  # 默認標記為單元測試
]