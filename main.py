#!/usr/bin/env python3
"""
LangGraph任務規劃器Demo主程序

這個文件展示了如何使用LangGraph任務規劃器的基本用法
"""

import sys
import os
from typing import Optional

# 添加src目錄到Python路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.graph import run_planner, visualize_graph, get_execution_trace
from src.schemas import PlannerConfig
from src.state import create_initial_state


def print_banner():
    """打印歡迎橫幅"""
    print("\n" + "="*60)
    print("🚀 LangGraph 智能任務規劃助手 Demo")
    print("="*60)
    print("本demo展示了LangGraph的核心功能：")
    print("• StateGraph工作流構建")
    print("• 節點和邊的設計模式")
    print("• 條件邏輯和分支控制")
    print("• 狀態管理和數據流")
    print("• 迭代優化機制")
    print("="*60 + "\n")


def print_section_header(title: str):
    """打印章節標題"""
    print(f"\n📋 {title}")
    print("-" * 50)


def print_result_summary(result: dict):
    """打印結果摘要"""
    print_section_header("執行結果摘要")
    
    # 基本信息
    execution_plan = result.get("execution_plan")
    if execution_plan:
        print(f"✅ 計劃標題: {execution_plan.title}")
        print(f"⏱️ 預估時間: {execution_plan.estimated_total_hours:.1f} 小時")
        print(f"📅 預計週期: {(execution_plan.estimated_end_date - execution_plan.estimated_start_date).days} 天")
        print(f"📊 包含階段: {len(execution_plan.phases)} 個")
        print(f"🎯 里程碑: {len(execution_plan.milestones)} 個")
    
    # 任務信息
    subtasks = result.get("subtasks", [])
    if subtasks:
        print(f"📝 任務總數: {len(subtasks)} 個")
        difficulty_count = {}
        for task in subtasks:
            difficulty_count[task.difficulty] = difficulty_count.get(task.difficulty, 0) + 1
        
        print("📊 難度分佈:")
        for difficulty, count in difficulty_count.items():
            print(f"   • {difficulty}: {count} 個")
    
    # 分析結果
    task_analysis = result.get("task_analysis")
    if task_analysis:
        print(f"🔍 複雜度評分: {task_analysis.complexity_score:.1f}/10")
        print(f"✅ 可行性評分: {task_analysis.feasibility_score:.1f}/10")
        if task_analysis.potential_blockers:
            print(f"⚠️ 潛在阻礙: {len(task_analysis.potential_blockers)} 個")
    
    # 迭代信息
    iteration_count = result.get("iteration_count", 0)
    is_approved = result.get("is_plan_approved", False)
    print(f"🔄 優化迭代: {iteration_count} 次")
    print(f"✅ 計劃狀態: {'已批准' if is_approved else '待優化'}")


def print_detailed_plan(result: dict):
    """打印詳細計劃"""
    execution_plan = result.get("execution_plan")
    if not execution_plan:
        print("❌ 沒有生成執行計劃")
        return
    
    print_section_header("詳細執行計劃")
    
    # 階段信息
    print("📋 執行階段:")
    for i, phase in enumerate(execution_plan.phases, 1):
        print(f"   {i}. {phase['phase_name']}")
        print(f"      📝 任務: {len(phase['tasks'])} 個")
        print(f"      ⏱️ 預估: {phase['estimated_hours']:.1f} 小時")
        print(f"      📄 說明: {phase['description']}")
    
    # 風險和建議
    if execution_plan.risks:
        print("\n⚠️ 識別的風險:")
        for risk in execution_plan.risks:
            print(f"   • {risk}")
    
    if execution_plan.recommendations:
        print("\n💡 執行建議:")
        for rec in execution_plan.recommendations:
            print(f"   • {rec}")
    
    # 里程碑
    if execution_plan.milestones:
        print("\n🎯 關鍵里程碑:")
        for milestone in execution_plan.milestones:
            print(f"   • {milestone['name']} - {milestone['date'][:10]}")


def print_execution_trace(result: dict):
    """打印執行軌跡"""
    print_section_header("LangGraph執行軌跡")
    
    trace = get_execution_trace(result)
    for step in trace:
        print(f"   {step}")
    
    print("\n🔄 這個軌跡展示了LangGraph節點的執行順序和狀態變化")


def run_demo_example(goal: str, config: Optional[PlannerConfig] = None):
    """運行demo示例"""
    print_section_header(f"分析目標: {goal}")
    
    try:
        # 執行規劃器
        print("🔄 正在執行LangGraph工作流...")
        result = run_planner(goal, config)
        
        # 打印結果
        print_result_summary(result)
        print_detailed_plan(result)
        print_execution_trace(result)
        
        return result
        
    except Exception as e:
        print(f"❌ 執行出錯: {str(e)}")
        print("💡 提示: 這是一個demo，某些功能可能需要真實的LLM API")
        return None


def interactive_mode():
    """交互式模式"""
    print_section_header("交互式模式")
    print("💭 請輸入您的目標（輸入'quit'退出）:")
    
    while True:
        try:
            goal = input("\n🎯 您的目標: ").strip()
            
            if goal.lower() in ['quit', 'exit', 'q', '退出']:
                print("👋 謝謝使用！")
                break
            
            if not goal:
                print("❌ 請輸入有效的目標")
                continue
            
            # 詢問配置選項
            print("\n⚙️ 配置選項:")
            print("1. 快速模式（自動批准簡單計劃）")
            print("2. 標準模式（包含反饋循環）")
            print("3. 詳細模式（最多迭代優化）")
            
            mode = input("選擇模式 (1-3, 默認2): ").strip() or "2"
            
            # 創建配置
            if mode == "1":
                config = PlannerConfig(
                    max_iterations=1,
                    auto_approve_simple_plans=True,
                    complexity_threshold=8.0
                )
            elif mode == "3":
                config = PlannerConfig(
                    max_iterations=5,
                    auto_approve_simple_plans=False,
                    complexity_threshold=5.0,
                    include_detailed_timeline=True
                )
            else:
                config = PlannerConfig()  # 默認配置
            
            # 運行demo
            run_demo_example(goal, config)
            
        except KeyboardInterrupt:
            print("\n\n👋 用戶中斷，退出程序")
            break
        except Exception as e:
            print(f"❌ 發生錯誤: {str(e)}")


def run_preset_examples():
    """運行預設示例"""
    print_section_header("預設示例演示")
    
    examples = [
        {
            "goal": "學習機器學習並找到相關工作",
            "description": "展示學習類目標的分解和規劃",
            "config": PlannerConfig(auto_approve_simple_plans=False)
        },
        {
            "goal": "開發一個個人博客網站",
            "description": "展示項目類目標的階段性規劃",
            "config": PlannerConfig(include_detailed_timeline=True)
        },
        {
            "goal": "提升英語口語能力",
            "description": "展示技能提升類目標的優化",
            "config": PlannerConfig(
                max_iterations=3,
                complexity_threshold=6.0
            )
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n🎯 示例 {i}: {example['description']}")
        print(f"目標: {example['goal']}")
        
        result = run_demo_example(example['goal'], example['config'])
        
        if result and i < len(examples):
            input("\n⏸️ 按Enter繼續下一個示例...")


def show_graph_visualization():
    """展示圖結構可視化"""
    print_section_header("LangGraph結構可視化")
    
    print("🏗️ 可用的圖類型:")
    graph_types = {
        "1": ("simple", "簡化版 - 線性工作流"),
        "2": ("standard", "標準版 - 包含反饋循環"),
        "3": ("advanced", "高級版 - 並行處理和複雜邏輯")
    }
    
    for key, (graph_type, desc) in graph_types.items():
        print(f"   {key}. {desc}")
    
    choice = input("\n選擇要查看的圖類型 (1-3): ").strip()
    
    if choice in graph_types:
        graph_type, desc = graph_types[choice]
        print(f"\n📊 {desc}")
        visualization = visualize_graph(graph_type)
        print(visualization)
    else:
        print("❌ 無效選擇")


def main():
    """主函數"""
    print_banner()
    
    if len(sys.argv) > 1:
        # 命令行模式
        goal = " ".join(sys.argv[1:])
        run_demo_example(goal)
    else:
        # 菜單模式
        while True:
            print("\n🎛️ 請選擇操作:")
            print("1. 運行預設示例")
            print("2. 交互式輸入目標")
            print("3. 查看LangGraph結構")
            print("4. 退出")
            
            choice = input("\n請選擇 (1-4): ").strip()
            
            if choice == "1":
                run_preset_examples()
            elif choice == "2":
                interactive_mode()
            elif choice == "3":
                show_graph_visualization()
            elif choice == "4":
                print("👋 謝謝使用LangGraph任務規劃器Demo！")
                break
            else:
                print("❌ 無效選擇，請重新輸入")


if __name__ == "__main__":
    main()