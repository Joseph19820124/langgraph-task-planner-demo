#!/usr/bin/env python3
"""
數據結構測試

測試Pydantic模型的驗證、序列化和業務邏輯。
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from src.schemas import (
    TaskDifficulty,
    TaskStatus,
    Task,
    TaskAnalysis,
    ExecutionPlan,
    PlanFeedback,
    PlannerConfig
)


class TestTaskSchema:
    """測試Task模型"""
    
    def test_task_creation_valid(self):
        """測試有效任務創建"""
        task = Task(
            id="test_001",
            title="測試任務",
            description="這是一個測試任務",
            difficulty=TaskDifficulty.MEDIUM,
            estimated_hours=5.5
        )
        
        assert task.id == "test_001"
        assert task.title == "測試任務"
        assert task.difficulty == TaskDifficulty.MEDIUM
        assert task.estimated_hours == 5.5
        assert task.prerequisites == []  # 默認值
        assert task.skills_required == []  # 默認值
        assert task.status == TaskStatus.PENDING  # 默認值
    
    def test_task_with_prerequisites(self):
        """測試帶前置條件的任務"""
        task = Task(
            id="task_002",
            title="依賴任務",
            description="依賴其他任務的任務",
            difficulty=TaskDifficulty.HARD,
            estimated_hours=10.0,
            prerequisites=["task_001"],
            skills_required=["高級技能"]
        )
        
        assert task.prerequisites == ["task_001"]
        assert task.skills_required == ["高級技能"]
    
    def test_task_validation_errors(self):
        """測試任務驗證錯誤"""
        # 負數小時
        with pytest.raises(ValidationError) as exc_info:
            Task(
                id="invalid",
                title="無效任務",
                description="測試",
                difficulty=TaskDifficulty.EASY,
                estimated_hours=-1.0  # 無效：負數
            )
        
        error = exc_info.value
        assert "estimated_hours" in str(error)
        
        # 零小時
        with pytest.raises(ValidationError):
            Task(
                id="invalid2",
                title="無效任務2",
                description="測試",
                difficulty=TaskDifficulty.EASY,
                estimated_hours=0.0  # 無效：零
            )
    
    def test_task_difficulty_enum(self):
        """測試難度枚舉"""
        difficulties = [
            TaskDifficulty.EASY,
            TaskDifficulty.MEDIUM,
            TaskDifficulty.HARD,
            TaskDifficulty.EXPERT
        ]
        
        for difficulty in difficulties:
            task = Task(
                id=f"task_{difficulty.value}",
                title=f"任務-{difficulty.value}",
                description="測試",
                difficulty=difficulty,
                estimated_hours=5.0
            )
            assert task.difficulty == difficulty
    
    def test_task_status_enum(self):
        """測試狀態枚舉"""
        statuses = [
            TaskStatus.PENDING,
            TaskStatus.IN_PROGRESS,
            TaskStatus.COMPLETED,
            TaskStatus.BLOCKED
        ]
        
        for status in statuses:
            task = Task(
                id=f"task_{status.value}",
                title="測試任務",
                description="測試",
                difficulty=TaskDifficulty.EASY,
                estimated_hours=1.0,
                status=status
            )
            assert task.status == status


class TestTaskAnalysisSchema:
    """測試TaskAnalysis模型"""
    
    def test_task_analysis_creation(self):
        """測試任務分析創建"""
        analysis = TaskAnalysis(
            total_tasks=5,
            total_estimated_hours=25.5,
            difficulty_distribution={
                TaskDifficulty.EASY: 2,
                TaskDifficulty.MEDIUM: 2,
                TaskDifficulty.HARD: 1
            },
            skill_requirements={
                "Python": 3,
                "Web開發": 2,
                "數據庫": 1
            },
            critical_path=["task_001", "task_003"],
            potential_blockers=["task_003"],
            complexity_score=7.5,
            feasibility_score=8.0
        )
        
        assert analysis.total_tasks == 5
        assert analysis.total_estimated_hours == 25.5
        assert len(analysis.difficulty_distribution) == 3
        assert analysis.complexity_score == 7.5
        assert analysis.feasibility_score == 8.0
    
    def test_score_validation(self):
        """測試評分驗證"""
        # 測試有效評分
        valid_scores = [0.0, 5.5, 10.0]
        for score in valid_scores:
            analysis = TaskAnalysis(
                total_tasks=1,
                total_estimated_hours=1.0,
                difficulty_distribution={},
                skill_requirements={},
                critical_path=[],
                potential_blockers=[],
                complexity_score=score,
                feasibility_score=score
            )
            assert analysis.complexity_score == score
            assert analysis.feasibility_score == score
        
        # 測試無效評分
        invalid_scores = [-0.1, 10.1, 15.0]
        for score in invalid_scores:
            with pytest.raises(ValidationError):
                TaskAnalysis(
                    total_tasks=1,
                    total_estimated_hours=1.0,
                    difficulty_distribution={},
                    skill_requirements={},
                    critical_path=[],
                    potential_blockers=[],
                    complexity_score=score,  # 無效評分
                    feasibility_score=5.0
                )


class TestExecutionPlanSchema:
    """測試ExecutionPlan模型"""
    
    def test_execution_plan_creation(self):
        """測試執行計劃創建"""
        start_date = datetime(2024, 1, 1, 9, 0)
        end_date = datetime(2024, 2, 1, 18, 0)
        
        plan = ExecutionPlan(
            plan_id="plan_001",
            title="測試計劃",
            description="這是一個測試執行計劃",
            estimated_start_date=start_date,
            estimated_end_date=end_date,
            estimated_total_hours=100.0
        )
        
        assert plan.plan_id == "plan_001"
        assert plan.title == "測試計劃"
        assert plan.estimated_start_date == start_date
        assert plan.estimated_end_date == end_date
        assert plan.estimated_total_hours == 100.0
        assert plan.version == 1  # 默認版本
        assert isinstance(plan.created_at, datetime)
    
    def test_execution_plan_with_phases(self):
        """測試帶階段的執行計劃"""
        phases = [
            {
                "phase_name": "階段1",
                "tasks": ["task_001", "task_002"],
                "estimated_hours": 20.0,
                "description": "第一階段"
            },
            {
                "phase_name": "階段2",
                "tasks": ["task_003"],
                "estimated_hours": 15.0,
                "description": "第二階段"
            }
        ]
        
        plan = ExecutionPlan(
            plan_id="plan_002",
            title="分階段計劃",
            description="包含多個階段的計劃",
            estimated_start_date=datetime.now(),
            estimated_end_date=datetime.now() + timedelta(days=30),
            estimated_total_hours=35.0,
            phases=phases
        )
        
        assert len(plan.phases) == 2
        assert plan.phases[0]["phase_name"] == "階段1"
        assert plan.phases[1]["estimated_hours"] == 15.0
    
    def test_execution_plan_with_schedule(self):
        """測試帶日程的執行計劃"""
        daily_schedule = {
            "2024-01-01": ["task_001"],
            "2024-01-02": ["task_002", "task_003"],
            "2024-01-03": ["task_004"]
        }
        
        plan = ExecutionPlan(
            plan_id="plan_003",
            title="日程計劃",
            description="包含詳細日程的計劃",
            estimated_start_date=datetime(2024, 1, 1),
            estimated_end_date=datetime(2024, 1, 10),
            estimated_total_hours=40.0,
            daily_schedule=daily_schedule
        )
        
        assert len(plan.daily_schedule) == 3
        assert "2024-01-01" in plan.daily_schedule
        assert len(plan.daily_schedule["2024-01-02"]) == 2
    
    def test_execution_plan_json_serialization(self):
        """測試執行計劃JSON序列化"""
        plan = ExecutionPlan(
            plan_id="plan_json",
            title="JSON測試",
            description="測試JSON序列化",
            estimated_start_date=datetime(2024, 1, 1, 9, 0),
            estimated_end_date=datetime(2024, 1, 31, 18, 0),
            estimated_total_hours=50.0
        )
        
        # 測試序列化
        json_data = plan.dict()
        assert isinstance(json_data, dict)
        assert json_data["plan_id"] == "plan_json"
        
        # 日期應該被正確處理
        assert "estimated_start_date" in json_data
        assert "estimated_end_date" in json_data


class TestPlanFeedbackSchema:
    """測試PlanFeedback模型"""
    
    def test_feedback_creation(self):
        """測試反饋創建"""
        feedback = PlanFeedback(
            feedback_type="approval",
            rating=5,
            comments="很好的計劃！",
            approval_status=True
        )
        
        assert feedback.feedback_type == "approval"
        assert feedback.rating == 5
        assert feedback.comments == "很好的計劃！"
        assert feedback.approval_status is True
        assert isinstance(feedback.timestamp, datetime)
    
    def test_feedback_with_changes(self):
        """測試帶修改建議的反饋"""
        suggested_changes = [
            "縮短總體時間",
            "增加實踐環節",
            "調整任務順序"
        ]
        
        feedback = PlanFeedback(
            feedback_type="revision",
            rating=3,
            comments="需要一些調整",
            suggested_changes=suggested_changes,
            approval_status=False
        )
        
        assert feedback.feedback_type == "revision"
        assert len(feedback.suggested_changes) == 3
        assert "縮短總體時間" in feedback.suggested_changes
        assert feedback.approval_status is False
    
    def test_rating_validation(self):
        """測試評分驗證"""
        # 有效評分
        valid_ratings = [1, 2, 3, 4, 5]
        for rating in valid_ratings:
            feedback = PlanFeedback(
                feedback_type="test",
                rating=rating,
                comments="測試",
                approval_status=True
            )
            assert feedback.rating == rating
        
        # 無效評分
        invalid_ratings = [0, 6, -1, 10]
        for rating in invalid_ratings:
            with pytest.raises(ValidationError):
                PlanFeedback(
                    feedback_type="test",
                    rating=rating,  # 無效評分
                    comments="測試",
                    approval_status=True
                )


class TestPlannerConfigSchema:
    """測試PlannerConfig模型"""
    
    def test_config_creation_default(self):
        """測試默認配置創建"""
        config = PlannerConfig()
        
        assert config.max_iterations == 3
        assert config.use_llm is False
        assert config.complexity_threshold == 7.0
        assert config.auto_approve_simple_plans is True
        assert config.include_detailed_timeline is True
    
    def test_config_creation_custom(self):
        """測試自定義配置創建"""
        config = PlannerConfig(
            max_iterations=5,
            use_llm=True,
            llm_provider="openai",
            complexity_threshold=8.5,
            auto_approve_simple_plans=False,
            include_detailed_timeline=False
        )
        
        assert config.max_iterations == 5
        assert config.use_llm is True
        assert config.llm_provider == "openai"
        assert config.complexity_threshold == 8.5
        assert config.auto_approve_simple_plans is False
        assert config.include_detailed_timeline is False
    
    def test_config_validation(self):
        """測試配置驗證"""
        # 測試最大迭代次數限制
        with pytest.raises(ValidationError):
            PlannerConfig(max_iterations=0)  # 小於最小值
        
        with pytest.raises(ValidationError):
            PlannerConfig(max_iterations=15)  # 大於最大值
        
        # 測試複雜度閾值限制
        with pytest.raises(ValidationError):
            PlannerConfig(complexity_threshold=0.5)  # 小於最小值
        
        with pytest.raises(ValidationError):
            PlannerConfig(complexity_threshold=12.0)  # 大於最大值
    
    def test_config_extra_fields_forbidden(self):
        """測試禁止額外字段"""
        with pytest.raises(ValidationError) as exc_info:
            PlannerConfig(
                max_iterations=3,
                extra_field="not_allowed"  # 額外字段
            )
        
        error = exc_info.value
        assert "extra_field" in str(error)


class TestSchemaIntegration:
    """測試模型集成"""
    
    def test_task_in_execution_plan(self):
        """測試任務和執行計劃的集成"""
        # 創建任務
        tasks = [
            Task(
                id="task_001",
                title="任務1",
                description="第一個任務",
                difficulty=TaskDifficulty.EASY,
                estimated_hours=5.0
            ),
            Task(
                id="task_002",
                title="任務2",
                description="第二個任務",
                difficulty=TaskDifficulty.MEDIUM,
                estimated_hours=10.0
            )
        ]
        
        # 創建執行計劃，引用任務
        phases = [
            {
                "phase_name": "階段1",
                "tasks": [task.id for task in tasks],
                "estimated_hours": sum(task.estimated_hours for task in tasks),
                "description": f"包含{len(tasks)}個任務"
            }
        ]
        
        plan = ExecutionPlan(
            plan_id="integration_test",
            title="集成測試計劃",
            description="測試任務和計劃的集成",
            estimated_start_date=datetime.now(),
            estimated_end_date=datetime.now() + timedelta(days=7),
            estimated_total_hours=sum(task.estimated_hours for task in tasks),
            phases=phases
        )
        
        # 驗證集成
        assert len(plan.phases) == 1
        assert len(plan.phases[0]["tasks"]) == 2
        assert plan.estimated_total_hours == 15.0
        assert "task_001" in plan.phases[0]["tasks"]
        assert "task_002" in plan.phases[0]["tasks"]
    
    def test_complete_workflow_schemas(self):
        """測試完整工作流的模型"""
        # 1. 配置
        config = PlannerConfig(
            max_iterations=2,
            auto_approve_simple_plans=False
        )
        
        # 2. 任務
        task = Task(
            id="workflow_task",
            title="工作流任務",
            description="測試完整工作流",
            difficulty=TaskDifficulty.MEDIUM,
            estimated_hours=8.0
        )
        
        # 3. 分析
        analysis = TaskAnalysis(
            total_tasks=1,
            total_estimated_hours=8.0,
            difficulty_distribution={TaskDifficulty.MEDIUM: 1},
            skill_requirements={"測試技能": 1},
            critical_path=[task.id],
            potential_blockers=[],
            complexity_score=5.0,
            feasibility_score=8.0
        )
        
        # 4. 計劃
        plan = ExecutionPlan(
            plan_id="workflow_plan",
            title="工作流計劃",
            description="完整工作流測試計劃",
            estimated_start_date=datetime.now(),
            estimated_end_date=datetime.now() + timedelta(days=3),
            estimated_total_hours=analysis.total_estimated_hours
        )
        
        # 5. 反饋
        feedback = PlanFeedback(
            feedback_type="workflow_test",
            rating=4,
            comments="工作流測試通過",
            approval_status=True
        )
        
        # 驗證所有模型都創建成功
        assert config.max_iterations == 2
        assert task.estimated_hours == 8.0
        assert analysis.total_tasks == 1
        assert plan.estimated_total_hours == 8.0
        assert feedback.approval_status is True
        
        # 驗證數據一致性
        assert analysis.total_estimated_hours == task.estimated_hours
        assert plan.estimated_total_hours == analysis.total_estimated_hours


if __name__ == "__main__":
    pytest.main([__file__, "-v"])