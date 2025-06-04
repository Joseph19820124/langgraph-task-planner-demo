# LangGraph 智能任務規劃助手 Demo

一個展示LangGraph核心功能的演示項目，實現了智能任務規劃和優化功能。

## 🎯 項目概述

這個demo展示如何使用LangGraph構建一個智能任務規劃助手，它能夠：

- 📝 **分析用戶目標**: 理解用戶想要實現的目標
- 🔧 **任務分解**: 將複雜目標分解為可執行的子任務
- 📊 **難度評估**: 評估每個任務的難度、時間和依賴關係
- 📋 **生成計劃**: 創建詳細的執行計劃
- 🔄 **迭代優化**: 根據用戶反饋不斷改進計劃

## 🏗️ LangGraph 核心概念演示

本項目展示了以下LangGraph概念：

### 🔄 StateGraph
- 狀態定義和管理
- 節點間的狀態傳遞
- 狀態累積和更新

### 🎯 Node Functions
- 純函數節點設計
- 狀態輸入輸出處理
- 錯誤處理和驗證

### 🌐 Graph Structure
- 線性和條件邊的使用
- 分支邏輯控制
- 循環和迭代機制

### 📊 State Management
- 類型化狀態定義
- 狀態驗證和轉換
- 複雜數據結構管理

## 🚀 快速開始

### 安裝依賴
```bash
pip install -r requirements.txt
```

### 設置環境變量
```bash
# 如果要使用真實的LLM，請設置API密鑰
export OPENAI_API_KEY="your-api-key"
# 或者
export GEMINI_API_KEY="your-gemini-key"
```

### 運行Demo
```bash
python main.py
```

### 交互式示例
```bash
python examples/interactive_demo.py
```

## 📁 項目結構

```
langgraph-task-planner-demo/
├── src/
│   ├── __init__.py
│   ├── state.py          # 狀態定義
│   ├── schemas.py        # 數據結構
│   ├── nodes.py          # 節點實現
│   ├── graph.py          # 圖構建
│   └── utils.py          # 工具函數
├── examples/
│   ├── simple_demo.py    # 簡單示例
│   ├── interactive_demo.py # 交互式示例
│   └── advanced_demo.py  # 高級示例
├── tests/
│   ├── test_nodes.py
│   └── test_graph.py
├── main.py              # 主程序
├── requirements.txt     # 依賴列表
└── README.md           # 項目說明
```

## 🎓 學習重點

### 1. 狀態設計 (state.py)
學習如何設計類型化的狀態結構：
```python
class PlannerState(TypedDict):
    user_goal: str
    subtasks: List[Task]
    task_analysis: Optional[TaskAnalysis]
    execution_plan: Optional[ExecutionPlan]
    # ...更多狀態字段
```

### 2. 節點實現 (nodes.py)
理解節點函數的設計模式：
```python
def analyze_goal(state: PlannerState) -> PlannerState:
    # 節點邏輯實現
    return {"analyzed_goal": result}
```

### 3. 圖構建 (graph.py)
掌握LangGraph的圖構建方法：
```python
builder = StateGraph(PlannerState)
builder.add_node("analyze", analyze_goal)
builder.add_edge("analyze", "breakdown")
```

### 4. 條件邏輯
學習條件邊和分支控制：
```python
builder.add_conditional_edges(
    "evaluate",
    should_refine_plan,
    {"refine": "refine_plan", "complete": END}
)
```

## 📋 示例用法

### 基本示例
```python
from src.graph import create_planner_graph

# 創建規劃器
planner = create_planner_graph()

# 執行規劃
result = planner.invoke({
    "user_goal": "學習機器學習並找到相關工作"
})

print(result["execution_plan"])
```

### 交互式示例
```python
# 運行交互式demo
python examples/interactive_demo.py

# 輸入您的目標，系統會生成詳細的執行計劃
```

## 🛠️ 自定義和擴展

### 添加新節點
1. 在 `src/nodes.py` 中定義新節點函數
2. 在 `src/graph.py` 中添加到圖中
3. 更新狀態定義如需要

### 修改規劃邏輯
- 調整 `breakdown_tasks` 節點的分解策略
- 修改 `evaluate_tasks` 的評估標準
- 自定義 `create_plan` 的計劃生成邏輯

### 集成外部服務
- 添加真實的LLM調用
- 集成項目管理工具API
- 連接日曆和提醒服務

## 🔍 技術特色

### 🎯 設計模式
- **狀態機模式**: 清晰的狀態轉換邏輯
- **策略模式**: 可配置的節點行為
- **建造者模式**: 靈活的圖構建過程

### 🛡️ 最佳實踐
- **類型安全**: 完整的類型註解
- **錯誤處理**: 健壯的異常處理機制
- **測試覆蓋**: 完整的單元測試

### 🔧 性能考慮
- **狀態最小化**: 只保存必要的狀態信息
- **懶加載**: 按需執行複雜計算
- **緩存機制**: 避免重複計算

## 📚 學習資源

- [LangGraph官方文檔](https://langchain-ai.github.io/langgraph/)
- [原始靈感項目](https://github.com/Joseph19820124/gemini-fullstack-langgraph-quickstart)
- [詳細學習筆記](https://github.com/Joseph19820124/gemini-langgraph-agent-study-notes)

## 🤝 貢獻指南

歡迎提交Issue和Pull Request！

1. Fork 項目
2. 創建功能分支
3. 提交更改
4. 發起Pull Request

## 📄 許可證

MIT License - 自由使用和修改

---

> 💡 **學習提示**: 建議先運行simple_demo.py了解基本流程，再通過interactive_demo.py體驗完整功能，最後閱讀源代碼理解實現細節。

**Happy Coding with LangGraph! 🚀**