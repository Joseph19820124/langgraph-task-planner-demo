#!/usr/bin/env python3
"""
LangGraph圖結構測試

測試LangGraph的圖構建、執行和狀態管理，包括：
- 圖結構驗證
- 執行流程測試
- 錯誤處理測試
- 性能基準測試
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import pytest
import time
from unittest.mock import patch, MagicMock

from src.graph import (
    create_planner_graph,
    create_simple_planner_graph,
    create_advanced_planner_graph,
    run_planner,
    run_simple_planner,
    visualize_graph,
    get_execution_trace
)
from src.state import create_initial_state
from src.schemas import PlannerConfig


class TestGraphCreation:
    """測試圖創建"""
    
    def test_create_simple_graph(self):
        """測試創建簡化圖"""
        graph = create_simple_planner_graph()
        
        # 驗證圖結構
        assert graph is not None
        assert hasattr(graph, 'nodes')
        assert hasattr(graph, 'edges')
        assert graph.name == "simple_task_planner"
        
        # 驗證節點存在
        expected_nodes = {
            "analyze_goal", "breakdown_tasks", 
            "evaluate_tasks", "create_plan", "finalize"
        }
        actual_nodes = set(graph.nodes.keys())
        
        # 簡化圖應該包含核心節點
        for node in expected_nodes:
            assert node in actual_nodes, f"缺少節點: {node}"
    
    def test_create_standard_graph(self):
        """測試創建標準圖"""
        graph = create_planner_graph()
        
        assert graph is not None
        assert graph.name == "task_planner"
        
        # 標準圖應該包含更多節點
        expected_nodes = {
            "analyze_goal", "breakdown_tasks", "evaluate_tasks",
            "create_plan", "get_feedback", "refine_plan", 
            "finalize", "error_handler"
        }
        actual_nodes = set(graph.nodes.keys())
        
        for node in expected_nodes:
            assert node in actual_nodes, f"缺少節點: {node}"
    
    def test_create_advanced_graph(self):
        """測試創建高級圖"""
        graph = create_advanced_planner_graph()
        
        assert graph is not None
        assert graph.name == "advanced_task_planner"
        
        # 高級圖應該包含最多節點
        expected_nodes = {
            "analyze_goal", "breakdown_tasks", "evaluate_tasks",
            "create_plan", "get_feedback", "refine_plan",
            "finalize", "error_handler", "state_monitor",
            "parallel_analysis", "risk_assessment", "resource_check"
        }
        actual_nodes = set(graph.nodes.keys())
        
        for node in expected_nodes:
            assert node in actual_nodes, f"缺少節點: {node}"
    
    def test_graph_compilation(self):
        """測試圖編譯"""
        # 測試所有類型的圖都能正確編譯
        graphs = [
            create_simple_planner_graph(),
            create_planner_graph(),
            create_advanced_planner_graph()
        ]
        
        for graph in graphs:
            # 編譯後的圖應該有invoke方法
            assert hasattr(graph, 'invoke')
            assert callable(graph.invoke)
            
            # 應該有名稱屬性
            assert hasattr(graph, 'name')
            assert isinstance(graph.name, str)


class TestGraphExecution:
    """測試圖執行"""
    
    def test_simple_graph_execution(self):
        """測試簡化圖執行"""
        result = run_simple_planner("學習基礎編程")
        
        # 驗證基本執行結果
        assert isinstance(result, dict)
        assert "user_goal" in result
        assert result["user_goal"] == "學習基礎編程"
        
        # 應該包含處理結果
        assert "analyzed_goal" in result
        assert "subtasks" in result
        assert "execution_plan" in result
    
    def test_standard_graph_execution(self):
        """測試標準圖執行"""
        config = PlannerConfig(max_iterations=1)  # 限制迭代減少測試時間
        result = run_planner("開發個人網站", config)
        
        assert isinstance(result, dict)
        assert "user_goal" in result
        assert "execution_plan" in result
        
        # 檢查迭代相關字段
        assert "iteration_count" in result
        assert "is_plan_approved" in result
    
    def test_execution_with_different_configs(self):
        """測試不同配置的執行"""
        configs = [
            PlannerConfig(max_iterations=1, auto_approve_simple_plans=True),
            PlannerConfig(max_iterations=2, auto_approve_simple_plans=False),
            PlannerConfig(max_iterations=3, complexity_threshold=8.0)
        ]
        
        goal = "提升職業技能"
        
        for config in configs:
            result = run_planner(goal, config)
            
            assert isinstance(result, dict)
            assert "user_goal" in result
            assert result["user_goal"] == goal
            
            # 配置應該影響執行結果
            iteration_count = result.get("iteration_count", 0)
            assert iteration_count <= config.max_iterations
    
    def test_execution_state_flow(self):
        """測試執行狀態流"""
        graph = create_simple_planner_graph()
        initial_state = create_initial_state("測試目標")
        
        result = graph.invoke(initial_state)
        
        # 驗證狀態演進
        assert "current_phase" in result
        assert result["current_phase"] in [
            "completed", "goal_analysis_complete", 
            "task_breakdown_complete", "plan_creation_complete"
        ]
        
        # 驗證處理筆記記錄了執行過程
        processing_notes = result.get("processing_notes", [])
        assert len(processing_notes) > 0
        
        # 檢查關鍵階段是否被記錄
        notes_text = " ".join(processing_notes)
        assert "分析" in notes_text or "生成" in notes_text
    
    def test_execution_error_handling(self):
        """測試執行錯誤處理"""
        # 測試空目標
        result = run_simple_planner("")
        
        errors = result.get("errors", [])
        assert len(errors) > 0
        assert any("不能為空" in error for error in errors)
        
        # 測試極長目標
        very_long_goal = "a" * 2000
        result = run_simple_planner(very_long_goal)
        
        # 應該能處理而不崩潰
        assert isinstance(result, dict)
        assert "user_goal" in result


class TestGraphVisualization:
    """測試圖可視化"""
    
    def test_visualize_simple_graph(self):
        """測試簡化圖可視化"""
        viz = visualize_graph("simple")
        
        assert isinstance(viz, str)
        assert "simple" in viz.lower()
        assert "節點數量" in viz
        assert "邊數量" in viz
    
    def test_visualize_standard_graph(self):
        """測試標準圖可視化"""
        viz = visualize_graph("standard")
        
        assert isinstance(viz, str)
        assert "standard" in viz.lower()
        assert "錯誤處理" in viz
    
    def test_visualize_advanced_graph(self):
        """測試高級圖可視化"""
        viz = visualize_graph("advanced")
        
        assert isinstance(viz, str)
        assert "advanced" in viz.lower()
        assert "並行" in viz
    
    def test_execution_trace(self):
        """測試執行軌跡"""
        result = run_simple_planner("學習測試")
        trace = get_execution_trace(result)
        
        assert isinstance(trace, list)
        assert len(trace) > 0
        
        # 軌跡應該包含階段信息
        trace_text = " ".join(trace)
        assert "階段" in trace_text or "完成" in trace_text


class TestGraphPerformance:
    """測試圖性能"""
    
    def test_execution_time(self):
        """測試執行時間"""
        goal = "學習數據分析"
        config = PlannerConfig(max_iterations=1)
        
        start_time = time.time()
        result = run_planner(goal, config)
        execution_time = time.time() - start_time
        
        # 執行時間應該在合理範圍內（< 30秒）
        assert execution_time < 30.0, f"執行時間過長: {execution_time:.2f}秒"
        
        # 結果應該完整
        assert "execution_plan" in result
    
    def test_memory_usage(self):
        """測試內存使用"""
        import psutil
        import gc
        
        process = psutil.Process()
        
        # 清理內存
        gc.collect()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        # 執行多個圖實例
        for i in range(5):
            result = run_simple_planner(f"測試目標{i}")
            assert "execution_plan" in result
        
        gc.collect()
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        memory_increase = final_memory - initial_memory
        
        # 內存增長應該在合理範圍內（< 100MB）
        assert memory_increase < 100, f"內存增長過多: {memory_increase:.1f}MB"
    
    def test_concurrent_execution(self):
        """測試並發執行"""
        import threading
        import queue
        
        results_queue = queue.Queue()
        
        def run_test(goal_suffix):
            try:
                result = run_simple_planner(f"學習{goal_suffix}")
                results_queue.put((goal_suffix, result, None))
            except Exception as e:
                results_queue.put((goal_suffix, None, str(e)))
        
        # 創建多個線程
        threads = []
        for i in range(3):
            thread = threading.Thread(target=run_test, args=(f"主題{i}",))
            threads.append(thread)
            thread.start()
        
        # 等待所有線程完成
        for thread in threads:
            thread.join(timeout=30)  # 30秒超時
        
        # 收集結果
        results = []
        while not results_queue.empty():
            results.append(results_queue.get())
        
        assert len(results) == 3
        
        # 所有執行應該成功
        for goal_suffix, result, error in results:
            assert error is None, f"{goal_suffix} 執行失敗: {error}"
            assert result is not None
            assert "execution_plan" in result


class TestGraphRobustness:
    """測試圖健壯性"""
    
    def test_invalid_state_handling(self):
        """測試無效狀態處理"""
        graph = create_simple_planner_graph()
        
        # 測試無效狀態格式
        invalid_states = [
            {},  # 空狀態
            {"invalid": "field"},  # 無效字段
            {"user_goal": None},  # None值
            {"user_goal": 123},  # 錯誤類型
        ]
        
        for invalid_state in invalid_states:
            try:
                result = graph.invoke(invalid_state)
                # 應該返回包含錯誤的結果，而不是崩潰
                assert isinstance(result, dict)
                # 可能包含錯誤信息
                errors = result.get("errors", [])
                # 不強制要求錯誤，因為某些情況下可能會被處理
            except Exception as e:
                # 如果拋出異常，應該是預期的類型
                assert isinstance(e, (ValueError, TypeError, KeyError))
    
    def test_large_input_handling(self):
        """測試大輸入處理"""
        # 測試極長的目標
        very_long_goal = "學習" + "Python編程" * 100
        
        try:
            result = run_simple_planner(very_long_goal)
            
            # 應該能處理大輸入
            assert isinstance(result, dict)
            assert "user_goal" in result
            
            # 檢查是否有截斷或錯誤處理
            goal_in_result = result["user_goal"]
            assert isinstance(goal_in_result, str)
        
        except Exception as e:
            # 如果處理失敗，應該是資源限制相關的異常
            assert "memory" in str(e).lower() or "size" in str(e).lower()
    
    def test_repeated_execution(self):
        """測試重複執行"""
        goal = "學習重複測試"
        config = PlannerConfig(max_iterations=1)
        
        results = []
        
        # 重複執行多次
        for i in range(5):
            result = run_planner(goal, config)
            results.append(result)
            
            # 每次執行都應該成功
            assert "execution_plan" in result
            assert result["user_goal"] == goal
        
        # 檢查結果一致性（不要求完全相同，因為可能有隨機性）
        first_result = results[0]
        for result in results[1:]:
            # 基本結構應該一致
            assert set(result.keys()) >= set(first_result.keys())
            assert result["user_goal"] == first_result["user_goal"]


class TestGraphIntegration:
    """測試圖集成"""
    
    def test_graph_type_comparison(self):
        """測試不同圖類型比較"""
        goal = "學習Web開發"
        config = PlannerConfig(max_iterations=1)
        
        # 執行不同類型的圖
        simple_result = run_simple_planner(goal)
        standard_result = run_planner(goal, config)
        
        # 都應該成功執行
        assert "execution_plan" in simple_result
        assert "execution_plan" in standard_result
        
        # 標準版本應該包含更多功能
        assert "iteration_count" in standard_result
        assert "is_plan_approved" in standard_result
        
        # 簡化版本可能不包含這些字段
        # 但都應該有基本的執行計劃
        simple_plan = simple_result["execution_plan"]
        standard_plan = standard_result["execution_plan"]
        
        assert simple_plan.title is not None
        assert standard_plan.title is not None
    
    @patch('src.nodes.simulate_user_feedback')
    def test_feedback_integration(self, mock_feedback):
        """測試反饋集成"""
        from src.schemas import PlanFeedback
        
        # 模擬批准的反饋
        mock_feedback.return_value = PlanFeedback(
            feedback_type="approval",
            rating=5,
            comments="很好的計劃",
            approval_status=True
        )
        
        config = PlannerConfig(
            max_iterations=2,
            auto_approve_simple_plans=False
        )
        
        result = run_planner("測試反饋集成", config)
        
        # 應該包含反饋相關信息
        assert "is_plan_approved" in result
        # 由於模擬了批准反饋，計劃應該被批准
        # 注意：實際結果可能取決於複雜度評估
    
    def test_end_to_end_workflow(self):
        """測試端到端工作流"""
        # 測試複雜的端到端場景
        complex_goal = "成為全棧開發工程師並找到理想工作"
        
        config = PlannerConfig(
            max_iterations=2,
            auto_approve_simple_plans=False,
            complexity_threshold=6.0,
            include_detailed_timeline=True
        )
        
        start_time = time.time()
        result = run_planner(complex_goal, config)
        execution_time = time.time() - start_time
        
        # 驗證完整的執行結果
        assert isinstance(result, dict)
        assert "user_goal" in result
        assert "analyzed_goal" in result
        assert "subtasks" in result
        assert "task_analysis" in result
        assert "execution_plan" in result
        
        # 驗證執行時間合理
        assert execution_time < 60.0, f"端到端執行時間過長: {execution_time:.2f}秒"
        
        # 驗證結果質量
        subtasks = result["subtasks"]
        assert len(subtasks) > 0, "沒有生成任務"
        
        execution_plan = result["execution_plan"]
        assert execution_plan.estimated_total_hours > 0
        assert len(execution_plan.phases) > 0
        
        # 驗證任務邏輯性
        task_titles = [task.title for task in subtasks]
        assert len(set(task_titles)) == len(task_titles), "任務標題不應重複"


if __name__ == "__main__":
    # 運行測試
    pytest.main([__file__, "-v", "--tb=short"])