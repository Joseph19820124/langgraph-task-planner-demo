#!/usr/bin/env python3
"""
高級LangGraph演示

這個文件展示了LangGraph的高級特性和最佳實踐。
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import asyncio
import time
from typing import Dict, Any, List, Optional
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass

from src.graph import (
    create_advanced_planner_graph,
    create_planner_graph,
    run_planner
)
from src.state import create_initial_state, PlannerState
from src.schemas import PlannerConfig, Task, TaskDifficulty
from src.nodes import analyze_goal, breakdown_tasks, evaluate_tasks


@dataclass
class BenchmarkResult:
    """基準測試結果"""
    graph_type: str
    execution_time: float
    memory_usage: float
    task_count: int
    complexity_score: float
    success: bool
    error_message: Optional[str] = None


class AdvancedDemo:
    """高級演示類
    
    展示LangGraph的高級功能：
    - 性能基準測試
    - 並行執行比較
    - 自定義節點開發
    - 錯誤處理策略
    - 監控和調試
    """
    
    def __init__(self):
        self.results_history = []
    
    def print_header(self, title: str):
        """打印標題"""
        print(f"\n{'='*70}")
        print(f"🚀 {title}")
        print(f"{'='*70}")
    
    def print_subheader(self, title: str):
        """打印子標題"""
        print(f"\n📊 {title}")
        print("-" * 50)
    
    def benchmark_graph_performance(self):
        """基準測試圖性能"""
        self.print_header("LangGraph 性能基準測試")
        
        test_goals = [
            "學習Python基礎",
            "開發一個電商網站項目",
            "建立數據科學職業發展路徑",
            "創建個人品牌和社交媒體影響力",
            "掌握機器學習並應用到實際業務問題中"
        ]
        
        graph_configs = [
            ("simple", "簡化版", {"max_iterations": 1}),
            ("standard", "標準版", {"max_iterations": 2}),
            ("advanced", "高級版", {"max_iterations": 3})
        ]
        
        results = []
        
        for goal in test_goals:
            print(f"\n🎯 測試目標: {goal}")
            
            for graph_type, graph_name, config_params in graph_configs:
                print(f"   測試 {graph_name}...", end=" ")
                
                try:
                    # 創建配置
                    config = PlannerConfig(**config_params)
                    
                    # 測量執行時間和內存
                    start_time = time.time()
                    import psutil
                    process = psutil.Process()
                    start_memory = process.memory_info().rss / 1024 / 1024  # MB
                    
                    # 執行圖
                    result = run_planner(goal, config)
                    
                    end_time = time.time()
                    end_memory = process.memory_info().rss / 1024 / 1024  # MB
                    
                    # 計算指標
                    execution_time = end_time - start_time
                    memory_usage = end_memory - start_memory
                    task_count = len(result.get('subtasks', []))
                    
                    task_analysis = result.get('task_analysis')
                    complexity_score = task_analysis.complexity_score if task_analysis else 0.0
                    
                    benchmark = BenchmarkResult(
                        graph_type=graph_name,
                        execution_time=execution_time,
                        memory_usage=memory_usage,
                        task_count=task_count,
                        complexity_score=complexity_score,
                        success=True
                    )
                    
                    print(f"✅ {execution_time:.2f}s")
                    
                except Exception as e:
                    benchmark = BenchmarkResult(
                        graph_type=graph_name,
                        execution_time=0,
                        memory_usage=0,
                        task_count=0,
                        complexity_score=0,
                        success=False,
                        error_message=str(e)
                    )
                    print(f"❌ 失敗")
                
                results.append((goal, benchmark))
        
        # 分析結果
        self._analyze_benchmark_results(results)
    
    def _analyze_benchmark_results(self, results: List[tuple]):
        """分析基準測試結果"""
        self.print_subheader("性能分析報告")
        
        # 按圖類型分組
        by_graph_type = {}
        for goal, result in results:
            if result.graph_type not in by_graph_type:
                by_graph_type[result.graph_type] = []
            by_graph_type[result.graph_type].append(result)
        
        # 計算平均指標
        print(f"{'圖類型':<12} {'平均時間':<10} {'平均內存':<10} {'成功率':<8} {'平均任務數':<10}")
        print("-" * 60)
        
        for graph_type, results_list in by_graph_type.items():
            successful_results = [r for r in results_list if r.success]
            
            if successful_results:
                avg_time = sum(r.execution_time for r in successful_results) / len(successful_results)
                avg_memory = sum(r.memory_usage for r in successful_results) / len(successful_results)
                avg_tasks = sum(r.task_count for r in successful_results) / len(successful_results)
                success_rate = len(successful_results) / len(results_list) * 100
                
                print(f"{graph_type:<12} {avg_time:<10.2f} {avg_memory:<10.1f} {success_rate:<8.0f}% {avg_tasks:<10.1f}")
            else:
                print(f"{graph_type:<12} {'N/A':<10} {'N/A':<10} {'0%':<8} {'N/A':<10}")
        
        # 性能建議
        print("\n💡 性能建議:")
        print("   • 簡化版適合快速原型和簡單任務")
        print("   • 標準版提供最佳的功能性能平衡")
        print("   • 高級版適合複雜場景但資源消耗較高")
    
    def demonstrate_parallel_execution(self):
        """演示並行執行"""
        self.print_header("並行執行演示")
        
        goals = [
            "學習Web開發",
            "掌握數據分析",
            "提升英語水平",
            "學習投資理財",
            "建立健身習慣"
        ]
        
        # 順序執行
        print("🔄 順序執行測試...")
        start_time = time.time()
        sequential_results = []
        
        for goal in goals:
            try:
                result = run_planner(goal, PlannerConfig(max_iterations=1))
                sequential_results.append((goal, result, None))
            except Exception as e:
                sequential_results.append((goal, None, str(e)))
        
        sequential_time = time.time() - start_time
        
        # 並行執行
        print("⚡ 並行執行測試...")
        start_time = time.time()
        
        def run_single_planner(goal):
            try:
                result = run_planner(goal, PlannerConfig(max_iterations=1))
                return (goal, result, None)
            except Exception as e:
                return (goal, None, str(e))
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            parallel_results = list(executor.map(run_single_planner, goals))
        
        parallel_time = time.time() - start_time
        
        # 比較結果
        self.print_subheader("執行時間比較")
        print(f"順序執行時間: {sequential_time:.2f} 秒")
        print(f"並行執行時間: {parallel_time:.2f} 秒")
        print(f"性能提升: {(sequential_time / parallel_time - 1) * 100:.1f}%")
        
        # 成功率比較
        seq_success = len([r for r in sequential_results if r[1] is not None])
        par_success = len([r for r in parallel_results if r[1] is not None])
        
        print(f"\n📊 成功率比較:")
        print(f"順序執行: {seq_success}/{len(goals)} ({seq_success/len(goals)*100:.0f}%)")
        print(f"並行執行: {par_success}/{len(goals)} ({par_success/len(goals)*100:.0f}%)")
    
    def demonstrate_custom_nodes(self):
        """演示自定義節點開發"""
        self.print_header("自定義節點開發演示")
        
        # 定義自定義節點
        def custom_validation_node(state: PlannerState) -> Dict[str, Any]:
            """自定義驗證節點"""
            subtasks = state.get('subtasks', [])
            
            # 自定義驗證邏輯
            validation_errors = []
            validation_warnings = []
            
            # 檢查任務數量
            if len(subtasks) < 3:
                validation_warnings.append("任務數量較少，可能需要更詳細的分解")
            elif len(subtasks) > 15:
                validation_errors.append("任務數量過多，建議合併相關任務")
            
            # 檢查時間估計
            total_hours = sum(task.estimated_hours for task in subtasks)
            if total_hours > 500:
                validation_errors.append("總時間過長，建議分階段執行")
            
            # 檢查技能要求
            all_skills = set()
            for task in subtasks:
                all_skills.update(task.skills_required)
            
            if len(all_skills) > 10:
                validation_warnings.append("需要掌握的技能較多，學習曲線可能較陡")
            
            return {
                'validation_errors': validation_errors,
                'validation_warnings': validation_warnings,
                'validation_passed': len(validation_errors) == 0,
                'processing_notes': state.get('processing_notes', []) + 
                                  [f"自定義驗證完成：{len(validation_errors)} 個錯誤，{len(validation_warnings)} 個警告"]
            }
        
        def custom_optimization_node(state: PlannerState) -> Dict[str, Any]:
            """自定義優化節點"""
            subtasks = state.get('subtasks', [])
            
            # 優化任務順序
            optimized_tasks = []
            
            # 按依賴關係和難度排序
            remaining_tasks = subtasks.copy()
            
            while remaining_tasks:
                # 找到沒有未完成依賴的任務
                ready_tasks = []
                for task in remaining_tasks:
                    dependencies_met = all(
                        dep_id in [t.id for t in optimized_tasks] 
                        for dep_id in task.prerequisites
                    )
                    if dependencies_met:
                        ready_tasks.append(task)
                
                if not ready_tasks:
                    # 如果沒有ready的任務，說明有循環依賴，取第一個
                    ready_tasks = [remaining_tasks[0]]
                
                # 按難度排序（先易後難）
                ready_tasks.sort(key=lambda t: {
                    TaskDifficulty.EASY: 1,
                    TaskDifficulty.MEDIUM: 2, 
                    TaskDifficulty.HARD: 3,
                    TaskDifficulty.EXPERT: 4
                }.get(t.difficulty, 5))
                
                # 添加第一個任務
                next_task = ready_tasks[0]
                optimized_tasks.append(next_task)
                remaining_tasks.remove(next_task)
            
            return {
                'subtasks': optimized_tasks,
                'processing_notes': state.get('processing_notes', []) + 
                                  ["完成任務順序優化"]
            }
        
        # 測試自定義節點
        print("🔧 測試自定義節點...")
        
        # 創建測試狀態
        test_goal = "成為全棧開發工程師"
        initial_state = create_initial_state(test_goal)
        
        # 執行基本節點
        state = {**initial_state, **analyze_goal(initial_state)}
        state = {**state, **breakdown_tasks(state)}
        
        print(f"原始任務數量: {len(state.get('subtasks', []))}")
        
        # 執行自定義驗證節點
        state = {**state, **custom_validation_node(state)}
        
        validation_errors = state.get('validation_errors', [])
        validation_warnings = state.get('validation_warnings', [])
        
        print(f"\n🔍 驗證結果:")
        print(f"   驗證通過: {state.get('validation_passed', False)}")
        print(f"   錯誤數量: {len(validation_errors)}")
        print(f"   警告數量: {len(validation_warnings)}")
        
        for error in validation_errors:
            print(f"   ❌ {error}")
        for warning in validation_warnings:
            print(f"   ⚠️ {warning}")
        
        # 執行自定義優化節點
        original_task_ids = [task.id for task in state.get('subtasks', [])]
        state = {**state, **custom_optimization_node(state)}
        optimized_task_ids = [task.id for task in state.get('subtasks', [])]
        
        print(f"\n⚡ 優化結果:")
        print(f"   任務順序是否改變: {original_task_ids != optimized_task_ids}")
        
        # 顯示優化後的前幾個任務
        optimized_tasks = state.get('subtasks', [])
        print(f"   優化後的前5個任務:")
        for i, task in enumerate(optimized_tasks[:5], 1):
            print(f"      {i}. {task.title} ({task.difficulty})")
    
    def demonstrate_error_handling(self):
        """演示錯誤處理策略"""
        self.print_header("錯誤處理和容錯機制演示")
        
        # 創建會導致錯誤的場景
        error_scenarios = [
            ("", "空目標測試"),
            ("a" * 1000, "過長目標測試"),
            ("impossible_task_12345", "無效目標測試"),
            ("學習量子計算並在一天內掌握", "不現實目標測試")
        ]
        
        print("🧪 測試各種錯誤場景...")
        
        for goal, scenario_name in error_scenarios:
            print(f"\n🔍 {scenario_name}:")
            print(f"   目標: '{goal[:50]}{'...' if len(goal) > 50 else ''}'")
            
            try:
                # 創建配置以快速失敗
                config = PlannerConfig(
                    max_iterations=1,
                    auto_approve_simple_plans=True
                )
                
                result = run_planner(goal, config)
                
                # 檢查錯誤狀態
                errors = result.get('errors', [])
                warnings = result.get('warnings', [])
                
                if errors:
                    print(f"   ❌ 捕獲到 {len(errors)} 個錯誤:")
                    for error in errors[:3]:  # 只顯示前3個
                        print(f"      • {error}")
                else:
                    print(f"   ✅ 意外成功執行")
                
                if warnings:
                    print(f"   ⚠️ 收到 {len(warnings)} 個警告")
                
                # 檢查部分結果
                subtasks = result.get('subtasks', [])
                if subtasks:
                    print(f"   📝 仍生成了 {len(subtasks)} 個任務")
                
            except Exception as e:
                print(f"   💥 拋出異常: {type(e).__name__}: {str(e)[:100]}")
        
        print("\n💡 錯誤處理最佳實踐:")
        print("   • 在每個節點中添加輸入驗證")
        print("   • 使用try-catch包裝關鍵操作")
        print("   • 提供有意義的錯誤消息")
        print("   • 支持部分失敗的優雅降級")
        print("   • 記錄錯誤用於調試和監控")
    
    def demonstrate_monitoring_debugging(self):
        """演示監控和調試功能"""
        self.print_header("監控和調試功能演示")
        
        # 創建一個複雜的測試場景
        complex_goal = "建立一個包含AI功能的SaaS產品並實現商業化"
        
        print(f"🎯 複雜場景測試: {complex_goal}")
        
        # 創建詳細配置
        config = PlannerConfig(
            max_iterations=3,
            auto_approve_simple_plans=False,
            complexity_threshold=5.0,
            include_detailed_timeline=True
        )
        
        print("\n🔄 開始監控執行過程...")
        
        # 執行並監控
        start_time = time.time()
        
        try:
            result = run_planner(complex_goal, config)
            execution_time = time.time() - start_time
            
            # 性能監控
            self.print_subheader("性能監控報告")
            print(f"總執行時間: {execution_time:.2f} 秒")
            print(f"迭代次數: {result.get('iteration_count', 0)}")
            print(f"最終狀態: {result.get('current_phase', 'unknown')}")
            
            # 狀態分析
            subtasks = result.get('subtasks', [])
            task_analysis = result.get('task_analysis')
            
            if subtasks:
                total_hours = sum(task.estimated_hours for task in subtasks)
                avg_task_complexity = sum({
                    TaskDifficulty.EASY: 1,
                    TaskDifficulty.MEDIUM: 2,
                    TaskDifficulty.HARD: 3,
                    TaskDifficulty.EXPERT: 4
                }.get(task.difficulty, 2) for task in subtasks) / len(subtasks)
                
                print(f"生成任務數: {len(subtasks)}")
                print(f"總估計時間: {total_hours:.1f} 小時")
                print(f"平均任務複雜度: {avg_task_complexity:.1f}/4")
            
            if task_analysis:
                print(f"複雜度評分: {task_analysis.complexity_score:.1f}/10")
                print(f"可行性評分: {task_analysis.feasibility_score:.1f}/10")
            
            # 執行軌跡分析
            self.print_subheader("執行軌跡分析")
            
            processing_notes = result.get('processing_notes', [])
            print(f"處理步驟數: {len(processing_notes)}")
            
            if processing_notes:
                print("關鍵執行步驟:")
                for i, note in enumerate(processing_notes, 1):
                    print(f"   {i}. {note}")
            
            # 質量分析
            self.print_subheader("質量分析")
            
            errors = result.get('errors', [])
            warnings = result.get('warnings', [])
            
            print(f"錯誤數量: {len(errors)}")
            print(f"警告數量: {len(warnings)}")
            print(f"計劃批准狀態: {result.get('is_plan_approved', False)}")
            
            # 資源使用分析
            execution_plan = result.get('execution_plan')
            if execution_plan:
                duration = (execution_plan.estimated_end_date - execution_plan.estimated_start_date).days
                print(f"計劃執行週期: {duration} 天")
                print(f"計劃階段數: {len(execution_plan.phases)}")
                print(f"識別風險數: {len(execution_plan.risks)}")
        
        except Exception as e:
            print(f"❌ 執行失敗: {str(e)}")
            print("🔍 這是監控系統捕獲的異常")
    
    def run_comprehensive_demo(self):
        """運行綜合演示"""
        print("🌟 LangGraph 高級特性綜合演示")
        print("=" * 70)
        
        demos = [
            ("性能基準測試", self.benchmark_graph_performance),
            ("並行執行比較", self.demonstrate_parallel_execution),
            ("自定義節點開發", self.demonstrate_custom_nodes),
            ("錯誤處理機制", self.demonstrate_error_handling),
            ("監控和調試", self.demonstrate_monitoring_debugging)
        ]
        
        for i, (name, demo_func) in enumerate(demos, 1):
            print(f"\n{'>'*20} {i}/{len(demos)}: {name} {'<'*20}")
            
            try:
                demo_func()
            except Exception as e:
                print(f"❌ {name} 演示失敗: {str(e)}")
            except KeyboardInterrupt:
                print(f"\n🛑 用戶中斷 {name} 演示")
                if input("是否繼續下一個演示？(y/n): ").lower() != 'y':
                    break
            
            if i < len(demos):
                input("\n⏸️ 按Enter繼續下一個演示...")
        
        print("\n🎉 所有高級演示完成！")
        print("💡 這些演示展示了LangGraph在生產環境中的實際應用能力")


def main():
    """主函數"""
    try:
        import psutil
    except ImportError:
        print("❌ 需要安裝psutil庫用於性能監控")
        print("   運行: pip install psutil")
        return
    
    demo = AdvancedDemo()
    demo.run_comprehensive_demo()


if __name__ == "__main__":
    main()