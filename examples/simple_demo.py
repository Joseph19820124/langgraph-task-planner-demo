#!/usr/bin/env python3
"""
簡單LangGraph演示

這個文件展示了LangGraph的最基本用法，適合初學者理解核心概念。
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.graph import create_simple_planner_graph, run_simple_planner
from src.state import create_initial_state
from src.schemas import PlannerConfig


def simple_example():
    """最簡單的LangGraph使用示例"""
    print("🚀 LangGraph 簡單示例")
    print("=" * 40)
    
    # 1. 定義用戶目標
    user_goal = "學習Python編程基礎"
    print(f"📝 目標: {user_goal}")
    
    # 2. 創建簡化版圖
    print("\n🏗️ 創建LangGraph...")
    graph = create_simple_planner_graph()
    print(f"   節點數量: {len(graph.nodes)}")
    print(f"   圖名稱: {graph.name}")
    
    # 3. 創建初始狀態
    print("\n📊 創建初始狀態...")
    initial_state = create_initial_state(user_goal)
    print(f"   會話ID: {initial_state['session_id']}")
    print(f"   創建時間: {initial_state['created_at']}")
    
    # 4. 執行圖
    print("\n🔄 執行LangGraph工作流...")
    try:
        result = graph.invoke(initial_state)
        
        # 5. 展示結果
        print("\n✅ 執行完成！")
        print_simple_results(result)
        
    except Exception as e:
        print(f"❌ 執行出錯: {str(e)}")
        print("💡 這是正常的，因為這是一個演示版本")


def print_simple_results(result: dict):
    """打印簡化的結果"""
    print("\n📋 結果摘要:")
    print("-" * 30)
    
    # 目標分析
    analyzed_goal = result.get("analyzed_goal")
    if analyzed_goal:
        print(f"🎯 目標類型: {analyzed_goal.get('goal_type', 'unknown')}")
        print(f"📊 複雜度: {analyzed_goal.get('complexity_level', 'unknown')}")
        print(f"🔍 範圍: {analyzed_goal.get('estimated_scope', 'unknown')}")
    
    # 任務分解
    subtasks = result.get("subtasks", [])
    if subtasks:
        print(f"\n📝 生成任務: {len(subtasks)} 個")
        for i, task in enumerate(subtasks[:3], 1):  # 只顯示前3個
            print(f"   {i}. {task.title} ({task.difficulty})")
        if len(subtasks) > 3:
            print(f"   ... 還有 {len(subtasks) - 3} 個任務")
    
    # 分析結果
    task_analysis = result.get("task_analysis")
    if task_analysis:
        print(f"\n🔍 分析結果:")
        print(f"   總時間: {task_analysis.total_estimated_hours:.1f} 小時")
        print(f"   複雜度: {task_analysis.complexity_score:.1f}/10")
        print(f"   可行性: {task_analysis.feasibility_score:.1f}/10")
    
    # 執行計劃
    execution_plan = result.get("execution_plan")
    if execution_plan:
        print(f"\n📅 執行計劃: {execution_plan.title}")
        print(f"   開始日期: {execution_plan.estimated_start_date.strftime('%Y-%m-%d')}")
        print(f"   結束日期: {execution_plan.estimated_end_date.strftime('%Y-%m-%d')}")
        print(f"   執行階段: {len(execution_plan.phases)} 個")
    
    # 處理過程
    processing_notes = result.get("processing_notes", [])
    if processing_notes:
        print(f"\n📜 處理過程:")
        for note in processing_notes[-3:]:  # 只顯示最後3個
            print(f"   • {note}")


def step_by_step_example():
    """逐步演示LangGraph的執行過程"""
    print("\n🔍 逐步執行演示")
    print("=" * 40)
    
    user_goal = "建立個人健身計劃"
    print(f"📝 目標: {user_goal}")
    
    # 手動執行每個步驟
    from src.nodes import analyze_goal, breakdown_tasks, evaluate_tasks, create_plan
    
    # 步驟1: 分析目標
    print("\n🔄 步驟1: 分析目標")
    state = create_initial_state(user_goal)
    state = {**state, **analyze_goal(state)}
    print(f"   結果: {state.get('analyzed_goal', {}).get('goal_type', 'unknown')} 類型目標")
    
    # 步驟2: 分解任務
    print("\n🔄 步驟2: 分解任務")
    state = {**state, **breakdown_tasks(state)}
    subtasks = state.get('subtasks', [])
    print(f"   結果: 生成 {len(subtasks)} 個子任務")
    
    # 步驟3: 評估任務
    print("\n🔄 步驟3: 評估任務")
    state = {**state, **evaluate_tasks(state)}
    analysis = state.get('task_analysis')
    if analysis:
        print(f"   結果: 複雜度 {analysis.complexity_score:.1f}, 可行性 {analysis.feasibility_score:.1f}")
    
    # 步驟4: 創建計劃
    print("\n🔄 步驟4: 創建計劃")
    state = {**state, **create_plan(state)}
    plan = state.get('execution_plan')
    if plan:
        print(f"   結果: 創建了 {len(plan.phases)} 階段的執行計劃")
    
    print("\n✅ 所有步驟完成！")
    print("\n💡 這展示了LangGraph如何將複雜流程分解為簡單的節點函數")


def compare_approaches():
    """比較不同的LangGraph使用方式"""
    print("\n📊 不同方式比較")
    print("=" * 40)
    
    user_goal = "學習數據科學"
    
    # 方式1: 使用簡化圖
    print("🔵 方式1: 簡化圖（線性流程）")
    start_time = time.time()
    result1 = run_simple_planner(user_goal)
    time1 = time.time() - start_time
    print(f"   執行時間: {time1:.3f}秒")
    print(f"   生成任務: {len(result1.get('subtasks', []))} 個")
    
    # 方式2: 使用標準圖（帶配置）
    print("\n🟢 方式2: 標準圖（包含反饋）")
    from src.graph import run_planner
    config = PlannerConfig(max_iterations=1)  # 限制迭代減少演示時間
    start_time = time.time()
    result2 = run_planner(user_goal, config)
    time2 = time.time() - start_time
    print(f"   執行時間: {time2:.3f}秒")
    print(f"   生成任務: {len(result2.get('subtasks', []))} 個")
    print(f"   迭代次數: {result2.get('iteration_count', 0)}")
    
    print("\n📈 對比總結:")
    print(f"   簡化圖更快，標準圖功能更完整")
    print(f"   選擇取決於需求複雜度")


def main():
    """主函數"""
    import time
    
    print("🌟 LangGraph 簡單演示集合")
    print("=" * 50)
    
    demos = [
        ("基本使用", simple_example),
        ("逐步執行", step_by_step_example),
        ("方式比較", compare_approaches),
    ]
    
    for i, (name, func) in enumerate(demos, 1):
        print(f"\n{i}. {name}")
        try:
            func()
        except Exception as e:
            print(f"❌ {name} 執行出錯: {str(e)}")
        
        if i < len(demos):
            input("\n⏸️ 按Enter繼續下一個演示...")
    
    print("\n🎉 所有演示完成！")
    print("💡 接下來可以嘗試 interactive_demo.py 進行更多互動")


if __name__ == "__main__":
    main()