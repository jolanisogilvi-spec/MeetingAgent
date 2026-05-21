<template>
  <div class="app-layout" :class="{ collapsed: sidebarCollapsed }">
    <aside class="sidebar">
      <div class="brand">
        <span class="brand-logo">会</span>
        <span class="brand-text">会议智能体</span>
      </div>
      <nav class="nav">
        <router-link
          v-for="item in navItems"
          :key="item.name"
          :to="item.path"
          class="nav-item"
          :class="{ active: isActive(item) }"
        >
          <el-icon class="nav-icon"><component :is="item.icon" /></el-icon>
          <span>{{ item.title }}</span>
        </router-link>
      </nav>
      <div class="sidebar-footer">v0.1.0</div>
    </aside>
    <main class="main">
      <header class="topbar">
        <button
          class="topbar-menu"
          type="button"
          :aria-label="sidebarCollapsed ? '展开侧边栏' : '折叠侧边栏'"
          @click="sidebarCollapsed = !sidebarCollapsed"
        >
          <el-icon><Fold /></el-icon>
        </button>
        <div class="topbar-spacer"></div>
        <a
          class="topbar-docs"
          href="/docs"
          target="_blank"
          rel="noopener noreferrer"
          aria-label="打开接口文档"
        >
          <el-icon><Document /></el-icon>
          <span>接口文档</span>
          <el-icon class="topbar-docs-arrow"><TopRight /></el-icon>
        </a>
      </header>
      <section class="workspace">
        <router-view v-slot="{ Component }">
          <component :is="Component" />
        </router-view>
      </section>
    </main>
  </div>
</template>

<script setup>
import { computed, ref } from 'vue'
import { useRoute } from 'vue-router'
import {
  DataAnalysis,
  Calendar,
  List,
  UserFilled,
  Setting,
  Fold,
  Document,
  TopRight
} from '@element-plus/icons-vue'

const route = useRoute()
const sidebarCollapsed = ref(false)

const navItems = [
  { name: 'dashboard', path: '/dashboard', title: '数据看板', icon: DataAnalysis },
  { name: 'meetings', path: '/meetings', title: '会议', icon: Calendar },
  { name: 'tasks', path: '/tasks', title: '日程任务', icon: List },
  { name: 'org', path: '/org', title: '人员与部门', icon: UserFilled },
  { name: 'settings', path: '/settings', title: '设置', icon: Setting }
]

const currentTopName = computed(() => {
  return route.meta?.parent || route.name
})

function isActive(item) {
  return currentTopName.value === item.name
}
</script>

<style scoped>
.app-layout {
  display: flex;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  background: var(--color-navy);
}

.sidebar {
  width: 198px;
  flex-shrink: 0;
  background: linear-gradient(180deg, #072337 0%, #061222 100%);
  color: #e5e7eb;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 255, 255, 0.07);
  box-shadow: 8px 0 24px rgba(10, 21, 36, 0.18);
  transition: width 0.18s ease;
}

.brand {
  height: 66px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 26px;
  font-size: 20px;
  font-weight: 800;
  color: #fff;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
  position: relative;
}

.brand::after {
  display: none;
}

.brand-logo {
  width: 32px;
  height: 32px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #ffffff;
  background: linear-gradient(135deg, #1686d9, #12a894);
  border-radius: 7px;
  font-size: 15px;
  font-weight: 900;
  box-shadow: 0 10px 20px rgba(0, 160, 210, 0.22);
}

.brand-text {
  letter-spacing: 0;
  white-space: nowrap;
}

.nav {
  flex: 1;
  padding: 16px 8px;
  overflow-y: auto;
}

.nav-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 20px;
  margin-bottom: 8px;
  color: #a7c0d1;
  text-decoration: none;
  font-size: 14px;
  font-weight: 650;
  border: 1px solid transparent;
  border-radius: 7px;
  transition: background-color 0.15s, color 0.15s, border-color 0.15s;
  cursor: pointer;
}

.nav-item:hover {
  background: rgba(0, 186, 218, 0.08);
  color: #fff;
  border-color: rgba(125, 211, 252, 0.16);
}

.nav-item.active {
  background: rgba(4, 92, 112, 0.82);
  color: #fff;
  border-color: rgba(31, 213, 238, 0.62);
  box-shadow: none;
}

.nav-item.active::before {
  content: '';
  position: absolute;
  left: -8px;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #12d6f5;
  border-radius: 0 8px 8px 0;
}

.nav-icon {
  font-size: 17px;
  color: #7dd6e8;
}

.sidebar-footer {
  margin: 0 10px 12px;
  padding: 12px;
  font-size: 12px;
  color: #7f93a8;
  border: 1px solid rgba(125, 211, 252, 0.1);
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.03);
}

.collapsed .sidebar {
  width: 72px;
}

.collapsed .brand {
  justify-content: center;
  padding: 0;
}

.collapsed .brand-text,
.collapsed .nav-item span,
.collapsed .sidebar-footer {
  display: none;
}

.collapsed .nav {
  padding: 16px 8px;
}

.collapsed .nav-item {
  justify-content: center;
  padding: 12px 0;
}

.collapsed .nav-item.active::before {
  left: -8px;
}

.main {
  flex: 1;
  background: #edf5fb;
  overflow: auto;
  min-width: 0;
}

.topbar {
  height: 66px;
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 0 24px;
  background: rgba(255, 255, 255, 0.96);
  border-bottom: 1px solid #d9e5ee;
  box-shadow: 0 10px 30px rgba(34, 66, 92, 0.06);
  position: sticky;
  top: 0;
  z-index: 20;
}

.topbar-menu {
  width: 38px;
  height: 38px;
  flex: 0 0 38px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  color: #122238;
  background: #ffffff;
  border: 1px solid #d6e2ec;
  border-radius: 8px;
  cursor: pointer;
}

.topbar-menu {
  font-size: 20px;
}

.topbar-spacer {
  flex: 1;
}

.topbar-docs {
  height: 38px;
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 7px;
  padding: 0 13px;
  color: #075a72;
  background: #eefbff;
  border: 1px solid #9bd6e8;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 800;
  box-shadow: 0 8px 18px rgba(7, 150, 189, 0.08);
  transition: color 0.15s, background-color 0.15s, border-color 0.15s;
}

.topbar-docs:hover {
  color: #ffffff;
  background: #0796bd;
  border-color: #0796bd;
}

.topbar-docs-arrow {
  font-size: 12px;
}

.workspace {
  min-width: 0;
}

@media (max-width: 860px) {
  .app-layout {
    flex-direction: column;
    height: auto;
    min-height: 100vh;
  }

  .sidebar {
    width: 100%;
    min-height: auto;
  }

  .brand {
    height: 58px;
    padding: 0 14px;
  }

  .nav {
    display: flex;
    gap: 8px;
    padding: 10px;
    overflow-x: auto;
  }

  .nav-item {
    flex-shrink: 0;
    margin-bottom: 0;
  }

  .nav-item.active::before {
    display: none;
  }

  .sidebar-footer {
    display: none;
  }

  .topbar {
    height: 58px;
    padding: 0 14px;
  }

  .topbar-docs {
    padding: 0 10px;
  }

}

@media (max-width: 1024px) {
  .topbar-docs span,
  .topbar-docs-arrow {
    display: none;
  }

  .topbar-docs {
    width: 38px;
    padding: 0;
  }
}
</style>
