#!/usr/bin/env python3
"""
交互式LangGraph演示

這個文件提供了完整的交互式體驗，讓用戶可以深入探索LangGraph的功能。
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from typing import Dict, Any, Optional
import time
from datetime import datetime

from src.graph import (
    create_planner_graph, 
    create_simple_planner_graph,
    create_advanced_planner_graph,
    run_planner,
    visualize_graph,
    get_execution_trace
)
from src.state import create_initial_state
from src.schemas import PlannerConfig, TaskDifficulty


class InteractiveDemo:
    """交互式演示類
    
    封裝了所有交互式功能，展示面向對象的LangGraph使用方式
    """
    
    def __init__(self):
        self.session_history = []
        self.current_result = None
        self.config = PlannerConfig()
    
    def print_header(self, title: str):
        """打印標題"""
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")
    
    def print_subheader(self, title: str):
        """打印子標題"""
        print(f"\n📋 {title}")
        print("-" * 40)
    
    def get_user_input(self, prompt: str, default: str = "") -> str:
        """獲取用戶輸入"""
        if default:
            user_input = input(f"{prompt} (默認: {default}): ").strip()
            return user_input if user_input else default
        else:
            return input(f"{prompt}: ").strip()
    
    def setup_configuration(self):
        """配置設置"""
        self.print_subheader("配置LangGraph參數")
        
        print("⚙️ 當前配置:")
        print(f"   最大迭代次數: {self.config.max_iterations}")
        print(f"   自動批准簡單計劃: {self.config.auto_approve_simple_plans}")
        print(f"   複雜度閾值: {self.config.complexity_threshold}")
        print(f"   包含詳細時間線: {self.config.include_detailed_timeline}")
        
        if self.get_user_input("\n是否要修改配置？(y/n)", "n").lower() == 'y':
            try:
                max_iter = int(self.get_user_input("最大迭代次數", str(self.config.max_iterations)))
                auto_approve = self.get_user_input("自動批准簡單計劃 (y/n)", "y").lower() == 'y'
                complexity = float(self.get_user_input("複雜度閾值 (1-10)", str(self.config.complexity_threshold)))
                detailed = self.get_user_input("包含詳細時間線 (y/n)", "y").lower() == 'y'
                
                self.config = PlannerConfig(
                    max_iterations=max_iter,
                    auto_approve_simple_plans=auto_approve,
                    complexity_threshold=complexity,
                    include_detailed_timeline=detailed
                )
                print("✅ 配置已更新")
            except ValueError:
                print("❌ 配置格式錯誤，使用默認配置")
    
    def run_planning_session(self):
        """運行規劃會話"""
        self.print_subheader("開始新的規劃會話")
        
        # 獲取目標
        goal = self.get_user_input("請輸入您的目標")
        if not goal:
            print("❌ 目標不能為空")
            return
        
        # 選擇圖類型
        print("\n🏗️ 選擇LangGraph類型:")
        print("1. 簡化版 (線性流程)")
        print("2. 標準版 (包含反饋循環)")
        print("3. 高級版 (並行處理)")
        
        graph_choice = self.get_user_input("選擇圖類型 (1-3)", "2")
        
        # 創建圖
        if graph_choice == "1":
            graph = create_simple_planner_graph()
            graph_name = "簡化版"
        elif graph_choice == "3":
            graph = create_advanced_planner_graph()
            graph_name = "高級版"
        else:
            graph = create_planner_graph()
            graph_name = "標準版"
        
        print(f"\n🔧 使用 {graph_name} LangGraph")
        print(f"   節點數量: {len(graph.nodes)}")
        
        # 執行規劃
        print("\n🚀 開始執行...")
        start_time = time.time()
        
        try:
            # 創建初始狀態
            initial_state = create_initial_state(goal, self.config)
            
            # 執行圖
            result = graph.invoke(initial_state)
            
            execution_time = time.time() - start_time
            
            # 保存結果
            self.current_result = result
            self.session_history.append({
                'goal': goal,
                'graph_type': graph_name,
                'execution_time': execution_time,
                'result': result,
                'timestamp': datetime.now()
            })
            
            print(f"✅ 執行完成！耗時 {execution_time:.2f} 秒")
            
            # 顯示結果摘要
            self.show_results_summary()
            
        except Exception as e:
            print(f"❌ 執行失敗: {str(e)}")
            print("💡 這是演示版本，某些功能可能不完整")
    
    def show_results_summary(self):
        """顯示結果摘要"""
        if not self.current_result:
            print("❌ 沒有可顯示的結果")
            return
        
        result = self.current_result
        self.print_subheader("執行結果摘要")
        
        # 基本統計
        subtasks = result.get('subtasks', [])
        execution_plan = result.get('execution_plan')
        task_analysis = result.get('task_analysis')
        
        print(f"📊 基本統計:")
        print(f"   任務總數: {len(subtasks)}")
        print(f"   迭代次數: {result.get('iteration_count', 0)}")
        print(f"   計劃狀態: {'已批准' if result.get('is_plan_approved') else '待優化'}")
        
        if task_analysis:
            print(f"   複雜度評分: {task_analysis.complexity_score:.1f}/10")
            print(f"   可行性評分: {task_analysis.feasibility_score:.1f}/10")
            print(f"   預估總時間: {task_analysis.total_estimated_hours:.1f} 小時")
        
        if execution_plan:
            duration = (execution_plan.estimated_end_date - execution_plan.estimated_start_date).days
            print(f"   計劃週期: {duration} 天")
            print(f"   執行階段: {len(execution_plan.phases)} 個")
            print(f"   關鍵里程碑: {len(execution_plan.milestones)} 個")
    
    def show_detailed_results(self):
        """顯示詳細結果"""
        if not self.current_result:
            print("❌ 沒有可顯示的結果")
            return
        
        result = self.current_result
        
        while True:
            self.print_subheader("詳細結果查看")
            print("1. 查看任務分解")
            print("2. 查看執行計劃")
            print("3. 查看分析報告")
            print("4. 查看執行軌跡")
            print("5. 返回主菜單")
            
            choice = self.get_user_input("請選擇 (1-5)", "5")
            
            if choice == "1":
                self._show_task_breakdown(result)
            elif choice == "2":
                self._show_execution_plan(result)
            elif choice == "3":
                self._show_analysis_report(result)
            elif choice == "4":
                self._show_execution_trace(result)
            elif choice == "5":
                break
            else:
                print("❌ 無效選擇")
    
    def _show_task_breakdown(self, result: Dict[str, Any]):
        """顯示任務分解"""
        subtasks = result.get('subtasks', [])
        if not subtasks:
            print("❌ 沒有任務數據")
            return
        
        print("\n📝 任務分解詳情:")
        print(f"{'序號':<4} {'標題':<20} {'難度':<8} {'時間':<8} {'前置':<10}")
        print("-" * 60)
        
        for i, task in enumerate(subtasks, 1):
            prereq = ", ".join(task.prerequisites[:2])  # 只顯示前2個前置任務
            if len(task.prerequisites) > 2:
                prereq += "..."
            
            print(f"{i:<4} {task.title[:18]:<20} {task.difficulty:<8} {task.estimated_hours:<8.1f} {prereq:<10}")
        
        # 按難度統計
        difficulty_stats = {}
        for task in subtasks:
            difficulty_stats[task.difficulty] = difficulty_stats.get(task.difficulty, 0) + 1
        
        print("\n📊 難度分佈:")
        for difficulty, count in difficulty_stats.items():
            print(f"   {difficulty}: {count} 個任務")
    
    def _show_execution_plan(self, result: Dict[str, Any]):
        """顯示執行計劃"""
        execution_plan = result.get('execution_plan')
        if not execution_plan:
            print("❌ 沒有執行計劃")
            return
        
        print(f"\n📅 執行計劃: {execution_plan.title}")
        print(f"描述: {execution_plan.description}")
        print(f"開始時間: {execution_plan.estimated_start_date.strftime('%Y-%m-%d')}")
        print(f"結束時間: {execution_plan.estimated_end_date.strftime('%Y-%m-%d')}")
        print(f"總工時: {execution_plan.estimated_total_hours:.1f} 小時")
        
        # 階段信息
        if execution_plan.phases:
            print("\n🔄 執行階段:")
            for i, phase in enumerate(execution_plan.phases, 1):
                print(f"   階段 {i}: {phase['phase_name']}")
                print(f"           任務數: {len(phase['tasks'])}")
                print(f"           預估時間: {phase['estimated_hours']:.1f} 小時")
        
        # 風險和建議
        if execution_plan.risks:
            print("\n⚠️ 潛在風險:")
            for risk in execution_plan.risks:
                print(f"   • {risk}")
        
        if execution_plan.recommendations:
            print("\n💡 執行建議:")
            for rec in execution_plan.recommendations:
                print(f"   • {rec}")
    
    def _show_analysis_report(self, result: Dict[str, Any]):
        """顯示分析報告"""
        task_analysis = result.get('task_analysis')
        analyzed_goal = result.get('analyzed_goal')
        
        if analyzed_goal:
            print("\n🎯 目標分析:")
            print(f"   目標類型: {analyzed_goal.get('goal_type', 'unknown')}")
            print(f"   複雜度級別: {analyzed_goal.get('complexity_level', 'unknown')}")
            print(f"   估計範圍: {analyzed_goal.get('estimated_scope', 'unknown')}")
            print(f"   關鍵領域: {', '.join(analyzed_goal.get('key_domains', []))}")
        
        if task_analysis:
            print("\n📊 任務分析:")
            print(f"   任務總數: {task_analysis.total_tasks}")
            print(f"   總估計時間: {task_analysis.total_estimated_hours:.1f} 小時")
            print(f"   複雜度評分: {task_analysis.complexity_score:.1f}/10")
            print(f"   可行性評分: {task_analysis.feasibility_score:.1f}/10")
            
            if task_analysis.critical_path:
                print(f"   關鍵路徑: {len(task_analysis.critical_path)} 個關鍵任務")
            
            if task_analysis.potential_blockers:
                print(f"   潛在阻礙: {len(task_analysis.potential_blockers)} 個")
            
            # 技能需求
            if task_analysis.skill_requirements:
                print("\n🛠️ 技能需求統計:")
                sorted_skills = sorted(task_analysis.skill_requirements.items(), 
                                     key=lambda x: x[1], reverse=True)
                for skill, count in sorted_skills[:5]:  # 顯示前5個
                    print(f"   {skill}: {count} 次")
    
    def _show_execution_trace(self, result: Dict[str, Any]):
        """顯示執行軌跡"""
        print("\n🔍 LangGraph執行軌跡:")
        
        trace = get_execution_trace(result)
        for step in trace:
            print(f"   {step}")
        
        # 顯示狀態變化
        current_phase = result.get('current_phase', 'unknown')
        print(f"\n📍 最終階段: {current_phase}")
        
        # 處理筆記
        notes = result.get('processing_notes', [])
        if notes:
            print("\n📝 處理筆記:")
            for note in notes[-5:]:  # 顯示最後5條
                print(f"   • {note}")
    
    def show_session_history(self):
        """顯示會話歷史"""
        if not self.session_history:
            print("❌ 沒有歷史會話記錄")
            return
        
        self.print_subheader("會話歷史")
        
        print(f"{'序號':<4} {'時間':<16} {'目標':<25} {'圖類型':<8} {'用時':<8}")
        print("-" * 70)
        
        for i, session in enumerate(self.session_history, 1):
            timestamp = session['timestamp'].strftime('%m-%d %H:%M')
            goal = session['goal'][:23] + "..." if len(session['goal']) > 25 else session['goal']
            graph_type = session['graph_type'][:6]
            exec_time = f"{session['execution_time']:.1f}s"
            
            print(f"{i:<4} {timestamp:<16} {goal:<25} {graph_type:<8} {exec_time:<8}")
        
        # 選擇查看歷史結果
        choice = self.get_user_input(f"\n查看歷史結果 (1-{len(self.session_history)}, 空格跳過)", "")
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(self.session_history):
                self.current_result = self.session_history[idx]['result']
                print(f"✅ 已切換到第 {choice} 個會話結果")
            else:
                print("❌ 無效的會話編號")
    
    def show_graph_comparison(self):
        """顯示圖結構比較"""
        self.print_subheader("LangGraph結構比較")
        
        graphs = {
            "簡化版": create_simple_planner_graph(),
            "標準版": create_planner_graph(),
            "高級版": create_advanced_planner_graph()
        }
        
        print(f"{'類型':<8} {'節點數':<8} {'特點':<30}")
        print("-" * 50)
        
        features = {
            "簡化版": "線性流程，快速執行",
            "標準版": "包含反饋循環，平衡功能",
            "高級版": "並行處理，複雜邏輯"
        }
        
        for name, graph in graphs.items():
            node_count = len(graph.nodes)
            feature = features[name]
            print(f"{name:<8} {node_count:<8} {feature:<30}")
        
        # 選擇查看詳細結構
        choice = self.get_user_input("\n查看詳細結構 (簡化版/標準版/高級版)", "")
        
        if choice in graphs:
            visualization = visualize_graph(
                "simple" if choice == "簡化版" else 
                "standard" if choice == "標準版" else "advanced"
            )
            print(f"\n🏗️ {choice} 詳細結構:")
            print(visualization)
    
    def run_interactive_session(self):
        """運行交互式會話"""
        self.print_header("LangGraph 交互式演示")
        print("🎮 歡迎使用交互式演示！這裡你可以深入探索LangGraph的各種功能。")
        
        while True:
            print("\n🎛️ 主菜單:")
            print("1. 配置LangGraph參數")
            print("2. 開始新的規劃會話")
            print("3. 查看詳細結果")
            print("4. 會話歷史")
            print("5. 圖結構比較")
            print("6. 退出")
            
            choice = self.get_user_input("請選擇 (1-6)", "2")
            
            try:
                if choice == "1":
                    self.setup_configuration()
                elif choice == "2":
                    self.run_planning_session()
                elif choice == "3":
                    self.show_detailed_results()
                elif choice == "4":
                    self.show_session_history()
                elif choice == "5":
                    self.show_graph_comparison()
                elif choice == "6":
                    print("\n👋 謝謝使用LangGraph交互式演示！")
                    break
                else:
                    print("❌ 無效選擇")
            
            except KeyboardInterrupt:
                print("\n\n🛑 用戶中斷操作")
                if self.get_user_input("是否要退出程序？(y/n)", "n").lower() == 'y':
                    break
            except Exception as e:
                print(f"❌ 操作出錯: {str(e)}")
                print("💡 這是演示版本，某些功能可能不穩定")


def main():
    """主函數"""
    demo = InteractiveDemo()
    demo.run_interactive_session()


if __name__ == "__main__":
    main()