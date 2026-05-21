import { createRouter, createWebHistory } from 'vue-router'

import MainLayout from '@/layouts/MainLayout.vue'

const routes = [
  {
    path: '/',
    component: MainLayout,
    redirect: '/dashboard',
    children: [
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/dashboard/Dashboard.vue'),
        meta: { title: '数据看板' }
      },
      {
        path: 'meetings',
        name: 'meetings',
        component: () => import('@/views/meetings/MeetingList.vue'),
        meta: { title: '会议' }
      },
      {
        path: 'meetings/:id',
        name: 'meeting-detail',
        component: () => import('@/views/meetings/MeetingDetail.vue'),
        meta: { title: '会议详情', parent: 'meetings' }
      },
      {
        path: 'tasks',
        name: 'tasks',
        component: () => import('@/views/tasks/TaskList.vue'),
        meta: { title: '日程任务' }
      },
      {
        path: 'org',
        name: 'org',
        component: () => import('@/views/org/PeopleAndDepartments.vue'),
        meta: { title: '人员与部门' }
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/views/settings/Settings.vue'),
        meta: { title: '设置' }
      }
    ]
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router
