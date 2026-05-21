import axios from 'axios'
import { ElMessage } from 'element-plus'

const http = axios.create({
  baseURL: '/api',
  timeout: 600000
})

function showError(error) {
  let detail = '请求失败'
  if (error?.response?.data) {
    const data = error.response.data
    if (typeof data === 'string') {
      detail = data
    } else if (data?.detail) {
      detail = typeof data.detail === 'string' ? data.detail : JSON.stringify(data.detail)
    } else {
      detail = JSON.stringify(data)
    }
  } else if (error?.message) {
    detail = error.message
  }
  ElMessage.error(detail)
}

http.interceptors.response.use(
  (response) => {
    if (response.config?.returnFullResponse) return response
    return response.data
  },
  (error) => {
    // 对于 blob 响应，需要把错误响应体解析为 JSON
    if (
      error?.response &&
      error.response.data instanceof Blob &&
      error.response.data.type &&
      error.response.data.type.indexOf('json') !== -1
    ) {
      return error.response.data.text().then((text) => {
        try {
          error.response.data = JSON.parse(text)
        } catch (e) {
          error.response.data = { detail: text }
        }
        showError(error)
        return Promise.reject(error)
      })
    }
    showError(error)
    return Promise.reject(error)
  }
)

export { http }

export const healthApi = {
  check: () => http.get('/health')
}

export const settingsApi = {
  get: () => http.get('/settings'),
  updateLlm: (data) => http.put('/settings/llm', data),
  updateEmbedding: (data) => http.put('/settings/embedding', data),
  updateSpeech: (data) => http.put('/settings/speech', data),
  testLlm: (data) => http.post('/settings/test/llm', data),
  testEmbedding: (data) => http.post('/settings/test/embedding', data),
  testSpeech: (data) => http.post('/settings/test/speech', data)
}

export const departmentsApi = {
  list: () => http.get('/departments'),
  create: (data) => http.post('/departments', data),
  get: (id) => http.get(`/departments/${id}`),
  update: (id, data) => http.put(`/departments/${id}`, data),
  remove: (id) => http.delete(`/departments/${id}`)
}

export const peopleApi = {
  list: (params) => http.get('/people', { params }),
  create: (data) => http.post('/people', data),
  get: (id) => http.get(`/people/${id}`),
  update: (id, data) => http.put(`/people/${id}`, data),
  remove: (id) => http.delete(`/people/${id}`)
}

export const meetingsApi = {
  list: (params) => http.get('/meetings', { params }),
  create: (data) => http.post('/meetings', data),
  get: (id) => http.get(`/meetings/${id}`),
  update: (id, data) => http.put(`/meetings/${id}`, data),
  remove: (id) => http.delete(`/meetings/${id}`),
  generate: (id, formData) =>
    http.post(`/meetings/${id}/generate`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    }),
  exportWord: (id) =>
    http.post(`/meetings/${id}/export`, null, {
      responseType: 'blob',
      // 标记需要原始响应（保留 headers 以获取 Content-Disposition）
      returnFullResponse: true
    })
}

export const tasksApi = {
  list: (params) => http.get('/tasks', { params }),
  create: (data) => http.post('/tasks', data),
  update: (id, data) => http.put(`/tasks/${id}`, data),
  remove: (id) => http.delete(`/tasks/${id}`)
}
