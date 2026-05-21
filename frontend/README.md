# MeetingAgent Frontend

Vue 3 + Vite + Element Plus 前端项目。

## 启动

```bash
cd frontend
npm install
npm run dev
```

打开 http://localhost:8050

开发模式会通过 vite 代理把 `/api/*` 请求转发到 `http://localhost:8000`，因此请先启动后端服务。

## 目录结构

```
frontend/
├── index.html
├── package.json
├── vite.config.js
└── src/
    ├── main.js            # 入口
    ├── App.vue            # 极简根组件
    ├── api/index.js       # axios 实例 + 所有接口封装
    ├── router/index.js    # vue-router
    ├── stores/            # Pinia stores
    ├── layouts/
    │   └── MainLayout.vue # 左侧导航 + 右侧主区域
    ├── views/
    │   ├── meetings/      # 会议列表 + 详情
    │   ├── tasks/         # 日程任务
    │   ├── org/           # 人员与部门
    │   └── settings/      # 设置
    └── styles/global.css
```

## 约定

- 所有 axios 调用统一在 `src/api/index.js`
- HTTP 错误自动通过 ElMessage.error 显示后端返回的 detail
- 模型测试结果显示在卡片内 `<el-alert>`，禁止使用全局通知
- 长任务必须有 loading 状态
- 删除前使用 ElMessageBox.confirm 二次确认
