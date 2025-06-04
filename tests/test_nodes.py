#!/usr/bin/env python3
"""
LangGraph節點單元測試

展示如何為LangGraph節點編寫單元測試，包括：
- 狀態輸入輸出驗證
- 錯誤條件測試
- 邊界條件處理
- Mock和隔離測試
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime

from src.state import create_initial_state, PlannerState
from src.schemas import (
    PlannerConfig, 
    Task, 
    TaskDifficulty, 
    TaskAnalysis, 
    ExecutionPlan,
    PlanFeedback
)
from src.nodes import (
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


class TestAnalyzeGoal:
    """測試目標分析節點"""
    
    def test_analyze_goal_success(self):
        """測試正常目標分析"""
        # 準備測試數據
        state = create_initial_state("學習Python編程")
        
        # 執行節點
        result = analyze_goal(state)
        
        # 驗證結果
        assert "analyzed_goal" in result
        assert result["analyzed_goal"] is not None
        assert "goal_type" in result["analyzed_goal"]
        assert "complexity_level" in result["analyzed_goal"]
        assert "current_phase" in result
        assert result["current_phase"] == "goal_analysis_complete"
    
    def test_analyze_goal_empty_input(self):
        """測試空目標輸入"""
        state = create_initial_state("")
        
        result = analyze_goal(state)
        
        # 應該包含錯誤信息
        assert "errors" in result
        assert len(result["errors"]) > 0
        assert "用戶目標不能為空" in result["errors"][0]
    
    def test_analyze_goal_different_types(self):
        """測試不同類型的目標"""
        test_cases = [
            ("學習機器學習", "learning"),
            ("開發網站項目", "project"),
            ("找到好工作", "career"),
            ("提升生活質量", "general")
        ]
        
        for goal, expected_type in test_cases:
            state = create_initial_state(goal)
            result = analyze_goal(state)
            
            analyzed_goal = result.get("analyzed_goal", {})
            assert analyzed_goal.get("goal_type") == expected_type
    
    def test_analyze_goal_processing_notes(self):
        """測試處理筆記的添加"""
        state = create_initial_state("測試目標")
        
        result = analyze_goal(state)
        
        assert "processing_notes" in result
        notes = result["processing_notes"]
        assert isinstance(notes, list)
        assert any("成功分析目標" in note for note in notes)


class TestBreakdownTasks:
    """測試任務分解節點"""
    
    def test_breakdown_tasks_success(self):
        """測試正常任務分解"""
        # 準備有分析結果的狀態
        state = create_initial_state("學習Python")
        state["analyzed_goal"] = {
            "goal_type": "learning",
            "complexity_level": "medium",
            "original_goal": "學習Python"
        }
        
        result = breakdown_tasks(state)
        
        assert "subtasks" in result
        subtasks = result["subtasks"]
        assert isinstance(subtasks, list)
        assert len(subtasks) > 0
        
        # 驗證任務結構
        for task in subtasks:
            assert isinstance(task, Task)
            assert task.id is not None
            assert task.title is not None
            assert task.estimated_hours > 0
    
    def test_breakdown_tasks_missing_analysis(self):
        """測試缺少目標分析的情況"""
        state = create_initial_state("測試目標")
        # 故意不設置analyzed_goal
        
        result = breakdown_tasks(state)
        
        assert "errors" in result
        assert "需要先分析目標" in result["errors"][0]
    
    def test_breakdown_tasks_different_goal_types(self):
        """測試不同目標類型的任務分解"""
        goal_types = ["learning", "project", "career", "general"]
        
        for goal_type in goal_types:
            state = create_initial_state("測試目標")
            state["analyzed_goal"] = {
                "goal_type": goal_type,
                "complexity_level": "medium",
                "original_goal": "測試目標"
            }
            
            result = breakdown_tasks(state)
            
            assert "subtasks" in result
            subtasks = result["subtasks"]
            assert len(subtasks) > 0
            
            # 不同類型應該生成不同的任務
            task_titles = [task.title for task in subtasks]
            assert len(set(task_titles)) == len(task_titles)  # 所有標題應該唯一
    
    def test_task_id_assignment(self):
        """測試任務ID分配"""
        state = create_initial_state("測試目標")
        state["analyzed_goal"] = {
            "goal_type": "learning",
            "complexity_level": "simple"
        }
        
        result = breakdown_tasks(state)
        subtasks = result["subtasks"]
        
        # 驗證ID格式和唯一性
        task_ids = [task.id for task in subtasks]
        assert len(set(task_ids)) == len(task_ids)  # 所有ID唯一
        
        for task_id in task_ids:
            assert task_id.startswith(("learning_", "project_", "career_", "general_"))


class TestEvaluateTasks:
    """測試任務評估節點"""
    
    def test_evaluate_tasks_success(self):
        """測試正常任務評估"""
        # 準備測試任務
        tasks = [
            Task(
                id="test_01",
                title="測試任務1",
                description="描述1",
                difficulty=TaskDifficulty.EASY,
                estimated_hours=5.0,
                skills_required=["基礎技能"]
            ),
            Task(
                id="test_02",
                title="測試任務2",
                description="描述2",
                difficulty=TaskDifficulty.HARD,
                estimated_hours=20.0,
                skills_required=["高級技能", "專業技能"]
            )
        ]
        
        state = create_initial_state("測試")
        state["subtasks"] = tasks
        
        result = evaluate_tasks(state)
        
        assert "task_analysis" in result
        analysis = result["task_analysis"]
        assert isinstance(analysis, TaskAnalysis)
        assert analysis.total_tasks == 2
        assert analysis.total_estimated_hours == 25.0
        assert analysis.complexity_score >= 0
        assert analysis.feasibility_score >= 0
    
    def test_evaluate_tasks_empty_list(self):
        """測試空任務列表"""
        state = create_initial_state("測試")
        state["subtasks"] = []
        
        result = evaluate_tasks(state)
        
        assert "errors" in result
        assert "沒有可評估的任務" in result["errors"][0]
    
    def test_difficulty_distribution_calculation(self):
        """測試難度分佈計算"""
        tasks = [
            Task(
                id="easy_01", title="簡單1", description="", 
                difficulty=TaskDifficulty.EASY, estimated_hours=2.0
            ),
            Task(
                id="easy_02", title="簡單2", description="", 
                difficulty=TaskDifficulty.EASY, estimated_hours=3.0
            ),
            Task(
                id="hard_01", title="困難1", description="", 
                difficulty=TaskDifficulty.HARD, estimated_hours=15.0
            )
        ]
        
        state = create_initial_state("測試")
        state["subtasks"] = tasks
        
        result = evaluate_tasks(state)
        analysis = result["task_analysis"]
        
        assert analysis.difficulty_distribution[TaskDifficulty.EASY] == 2
        assert analysis.difficulty_distribution[TaskDifficulty.HARD] == 1
        assert analysis.difficulty_distribution.get(TaskDifficulty.MEDIUM, 0) == 0
    
    def test_warning_generation(self):
        """測試警告生成"""
        # 創建高複雜度場景
        tasks = []
        for i in range(10):
            tasks.append(Task(
                id=f"expert_{i:02d}",
                title=f"專家任務{i}",
                description="複雜任務",
                difficulty=TaskDifficulty.EXPERT,
                estimated_hours=50.0,
                skills_required=[f"技能{j}" for j in range(5)]
            ))
        
        state = create_initial_state("測試")
        state["subtasks"] = tasks
        
        result = evaluate_tasks(state)
        
        # 應該生成警告
        warnings = result.get("warnings", [])
        assert len(warnings) > 0
        
        # 檢查特定警告類型
        warning_text = " ".join(warnings)
        assert "複雜度較高" in warning_text or "工時較長" in warning_text


class TestCreatePlan:
    """測試計劃創建節點"""
    
    def test_create_plan_success(self):
        """測試正常計劃創建"""
        # 準備完整的狀態
        tasks = [
            Task(
                id="task_01", title="任務1", description="描述1",
                difficulty=TaskDifficulty.MEDIUM, estimated_hours=10.0
            )
        ]
        
        analysis = TaskAnalysis(
            total_tasks=1,
            total_estimated_hours=10.0,
            difficulty_distribution={TaskDifficulty.MEDIUM: 1},
            skill_requirements={"技能1": 1},
            critical_path=["task_01"],
            potential_blockers=[],
            complexity_score=5.0,
            feasibility_score=8.0
        )
        
        state = create_initial_state("測試")
        state["subtasks"] = tasks
        state["task_analysis"] = analysis
        state["analyzed_goal"] = {"original_goal": "測試目標"}
        
        result = create_plan(state)
        
        assert "execution_plan" in result
        plan = result["execution_plan"]
        assert isinstance(plan, ExecutionPlan)
        assert plan.plan_id is not None
        assert plan.estimated_total_hours == 10.0
        assert len(plan.phases) > 0
    
    def test_create_plan_missing_requirements(self):
        """測試缺少必要條件"""
        state = create_initial_state("測試")
        # 故意不設置subtasks和task_analysis
        
        result = create_plan(state)
        
        assert "errors" in result
        assert "需要完成任務分解和評估" in result["errors"][0]
    
    def test_plan_history_update(self):
        """測試計劃歷史更新"""
        tasks = [Task(
            id="task_01", title="任務1", description="",
            difficulty=TaskDifficulty.EASY, estimated_hours=5.0
        )]
        
        analysis = TaskAnalysis(
            total_tasks=1, total_estimated_hours=5.0,
            difficulty_distribution={TaskDifficulty.EASY: 1},
            skill_requirements={}, critical_path=[], potential_blockers=[],
            complexity_score=3.0, feasibility_score=9.0
        )
        
        state = create_initial_state("測試")
        state["subtasks"] = tasks
        state["task_analysis"] = analysis
        state["analyzed_goal"] = {"original_goal": "測試"}
        state["plan_history"] = []  # 空歷史
        
        result = create_plan(state)
        
        assert "plan_history" in result
        history = result["plan_history"]
        assert len(history) == 1
        assert isinstance(history[0], ExecutionPlan)


class TestConditionalFunctions:
    """測試條件函數"""
    
    def test_should_get_feedback_auto_approve(self):
        """測試自動批准簡單計劃"""
        config = PlannerConfig(
            auto_approve_simple_plans=True,
            complexity_threshold=7.0
        )
        
        analysis = TaskAnalysis(
            total_tasks=3, total_estimated_hours=15.0,
            difficulty_distribution={}, skill_requirements={},
            critical_path=[], potential_blockers=[],
            complexity_score=5.0,  # 低於閾值
            feasibility_score=8.0
        )
        
        state = create_initial_state("測試")
        state["config"] = config
        state["task_analysis"] = analysis
        
        result = should_get_feedback(state)
        assert result == "finalize"
    
    def test_should_get_feedback_need_feedback(self):
        """測試需要獲取反饋"""
        config = PlannerConfig(
            auto_approve_simple_plans=True,
            complexity_threshold=5.0
        )
        
        analysis = TaskAnalysis(
            total_tasks=10, total_estimated_hours=100.0,
            difficulty_distribution={}, skill_requirements={},
            critical_path=[], potential_blockers=[],
            complexity_score=8.0,  # 高於閾值
            feasibility_score=6.0
        )
        
        state = create_initial_state("測試")
        state["config"] = config
        state["task_analysis"] = analysis
        
        result = should_get_feedback(state)
        assert result == "get_feedback"
    
    def test_should_refine_plan_approved(self):
        """測試已批准的計劃"""
        feedback = PlanFeedback(
            feedback_type="approval",
            rating=5,
            comments="很好的計劃",
            approval_status=True
        )
        
        state = create_initial_state("測試")
        state["feedback"] = feedback
        
        result = should_refine_plan(state)
        assert result == "finalize"
    
    def test_should_refine_plan_max_iterations(self):
        """測試達到最大迭代次數"""
        config = PlannerConfig(max_iterations=3)
        
        feedback = PlanFeedback(
            feedback_type="revision",
            rating=3,
            comments="需要改進",
            approval_status=False
        )
        
        state = create_initial_state("測試")
        state["config"] = config
        state["feedback"] = feedback
        state["iteration_count"] = 3  # 達到最大次數
        
        result = should_refine_plan(state)
        assert result == "finalize"
    
    def test_should_refine_plan_continue(self):
        """測試需要繼續優化"""
        config = PlannerConfig(max_iterations=5)
        
        feedback = PlanFeedback(
            feedback_type="revision",
            rating=3,
            comments="需要改進",
            approval_status=False
        )
        
        state = create_initial_state("測試")
        state["config"] = config
        state["feedback"] = feedback
        state["iteration_count"] = 1
        
        result = should_refine_plan(state)
        assert result == "refine_plan"
    
    def test_has_errors_with_errors(self):
        """測試有錯誤的狀態"""
        state = create_initial_state("測試")
        state["errors"] = ["測試錯誤1", "測試錯誤2"]
        
        result = has_errors(state)
        assert result == "error_handler"
    
    def test_has_errors_no_errors(self):
        """測試無錯誤的狀態"""
        state = create_initial_state("測試")
        state["errors"] = []
        
        result = has_errors(state)
        assert result == "continue"


class TestErrorHandling:
    """測試錯誤處理"""
    
    def test_node_exception_handling(self):
        """測試節點異常處理"""
        # 創建會導致異常的狀態
        state = {"invalid": "state"}  # 無效狀態格式
        
        # 測試每個節點的異常處理
        result = analyze_goal(state)
        assert "errors" in result
        
        result = breakdown_tasks(state)
        assert "errors" in result
        
        result = evaluate_tasks(state)
        assert "errors" in result
        
        result = create_plan(state)
        assert "errors" in result
    
    @patch('src.nodes.simulate_user_feedback')
    def test_get_feedback_exception(self, mock_feedback):
        """測試反饋獲取異常處理"""
        mock_feedback.side_effect = Exception("模擬異常")
        
        plan = ExecutionPlan(
            plan_id="test", title="測試計劃", description="測試",
            estimated_start_date=datetime.now(),
            estimated_end_date=datetime.now(),
            estimated_total_hours=10.0
        )
        
        state = create_initial_state("測試")
        state["execution_plan"] = plan
        
        result = get_feedback(state)
        assert "errors" in result
        assert "反饋收集失敗" in result["errors"][0]


class TestIntegration:
    """集成測試"""
    
    def test_full_node_pipeline(self):
        """測試完整的節點流水線"""
        # 模擬完整的執行流程
        initial_state = create_initial_state("學習數據科學")
        
        # 1. 分析目標
        state = {**initial_state, **analyze_goal(initial_state)}
        assert "analyzed_goal" in state
        assert state.get("errors", []) == []
        
        # 2. 分解任務
        state = {**state, **breakdown_tasks(state)}
        assert "subtasks" in state
        assert len(state["subtasks"]) > 0
        
        # 3. 評估任務
        state = {**state, **evaluate_tasks(state)}
        assert "task_analysis" in state
        
        # 4. 創建計劃
        state = {**state, **create_plan(state)}
        assert "execution_plan" in state
        
        # 驗證最終狀態
        assert state.get("current_phase") == "plan_creation_complete"
        assert len(state.get("errors", [])) == 0
    
    def test_state_consistency(self):
        """測試狀態一致性"""
        state = create_initial_state("測試目標")
        
        # 確保初始狀態包含所有必要字段
        required_fields = [
            "user_goal", "subtasks", "task_analysis", "execution_plan",
            "feedback", "iteration_count", "is_plan_approved",
            "current_phase", "processing_notes", "errors", "session_id"
        ]
        
        for field in required_fields:
            assert field in state, f"缺少必要字段: {field}"
        
        # 測試狀態更新後的一致性
        updated_state = {**state, **analyze_goal(state)}
        
        # 新狀態應該保留原有字段並添加新字段
        for field in required_fields:
            assert field in updated_state
        
        # 檢查新增字段
        assert "analyzed_goal" in updated_state
        assert "last_updated" in updated_state


if __name__ == "__main__":
    # 運行測試
    pytest.main([__file__, "-v", "--tb=short"])