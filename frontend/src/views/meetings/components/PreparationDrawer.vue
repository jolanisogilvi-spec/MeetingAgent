<template>
  <el-drawer
    v-model="visible"
    title="会前准备"
    size="760px"
    destroy-on-close
    class="preparation-drawer"
  >
    <div v-loading="loading" class="prep-body">
      <section class="prep-section">
        <div class="section-head">
          <div>
            <h3>会议公共资料</h3>
            <p>上传所有参会人员会前都需要查看的资料</p>
          </div>
          <el-upload
            :auto-upload="false"
            :show-file-list="false"
            :on-change="(file) => uploadFile(file, 'common')"
            accept=".txt,.doc,.docx,.pdf,.ppt,.pptx,.xls,.xlsx"
          >
            <el-button type="primary" plain :icon="Upload">上传资料</el-button>
          </el-upload>
        </div>
        <div class="prep-files">
          <div v-if="!prep.common_files.length" class="empty-files">暂无公共资料</div>
          <div v-for="file in prep.common_files" :key="file.id" class="prep-file">
            <a :href="file.url" target="_blank" rel="noopener noreferrer">{{ file.name }}</a>
            <span>{{ formatSize(file.size) }}</span>
            <el-button link type="danger" @click="removeFile(file)">删除</el-button>
          </div>
        </div>
      </section>

      <section class="prep-section">
        <div class="section-head">
          <div>
            <h3>参会人员准备事项</h3>
            <p>为每位参会人员填写需要准备的资料、文件和状态</p>
          </div>
          <el-button type="success" :loading="saving" @click="savePreparation">保存准备内容</el-button>
        </div>

        <div v-if="participantRows.length" class="participant-list">
          <div v-for="person in participantRows" :key="person.id" class="participant-card">
            <div class="person-head">
              <div>
                <strong>{{ person.name }}</strong>
                <span>{{ person.role || '参会人员' }}</span>
              </div>
              <el-select v-model="participantPrep(person.id).status" size="small" style="width: 112px">
                <el-option label="未准备" value="未准备" />
                <el-option label="准备中" value="准备中" />
                <el-option label="已准备" value="已准备" />
              </el-select>
            </div>
            <el-input
              v-model="participantPrep(person.id).requirements"
              type="textarea"
              :rows="3"
              maxlength="2000"
              show-word-limit
              placeholder="填写该参会人员会前需要准备的资料、数据、文件或发言要点"
            />
            <div class="file-toolbar">
              <span>个人准备文件</span>
              <el-upload
                :auto-upload="false"
                :show-file-list="false"
                :on-change="(file) => uploadFile(file, 'participant', person.id)"
                accept=".txt,.doc,.docx,.pdf,.ppt,.pptx,.xls,.xlsx"
              >
                <el-button size="small" plain :icon="Upload">上传文件</el-button>
              </el-upload>
            </div>
            <div class="prep-files">
              <div v-if="!participantPrep(person.id).files.length" class="empty-files">
                暂无个人准备文件
              </div>
              <div
                v-for="file in participantPrep(person.id).files"
                :key="file.id"
                class="prep-file"
              >
                <a :href="file.url" target="_blank" rel="noopener noreferrer">{{ file.name }}</a>
                <span>{{ formatSize(file.size) }}</span>
                <el-button link type="danger" @click="removeFile(file)">删除</el-button>
              </div>
            </div>
          </div>
        </div>
        <el-empty v-else description="当前会议暂无参会人员" :image-size="80" />
      </section>
    </div>
  </el-drawer>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Upload } from '@element-plus/icons-vue'
import { meetingsApi } from '@/api'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  meeting: { type: Object, default: null },
  people: { type: Array, default: () => [] }
})
const emit = defineEmits(['update:modelValue'])

const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

const loading = ref(false)
const saving = ref(false)
const prep = reactive({
  common_files: [],
  participants: {}
})

const peopleMap = computed(() => Object.fromEntries(props.people.map((p) => [p.id, p])))
const participantRows = computed(() =>
  (props.meeting?.participant_ids || []).map((id) => peopleMap.value[id] || { id, name: id })
)

watch(
  () => props.modelValue,
  (open) => {
    if (open) loadPreparation()
  }
)

function applyPreparation(data) {
  prep.common_files = Array.isArray(data?.common_files) ? data.common_files : []
  prep.participants = data?.participants && typeof data.participants === 'object' ? data.participants : {}
  for (const person of participantRows.value) {
    participantPrep(person.id)
  }
}

function participantPrep(personId) {
  if (!prep.participants[personId]) {
    prep.participants[personId] = {
      requirements: '',
      status: '未准备',
      files: []
    }
  }
  if (!Array.isArray(prep.participants[personId].files)) {
    prep.participants[personId].files = []
  }
  if (!prep.participants[personId].status) {
    prep.participants[personId].status = '未准备'
  }
  return prep.participants[personId]
}

async function loadPreparation() {
  if (!props.meeting?.id) return
  loading.value = true
  try {
    const data = await meetingsApi.getPreparation(props.meeting.id)
    applyPreparation(data)
  } finally {
    loading.value = false
  }
}

function buildPayload() {
  const currentIds = new Set(props.meeting?.participant_ids || [])
  const participants = {}
  for (const personId of currentIds) {
    const entry = participantPrep(personId)
    participants[personId] = {
      requirements: entry.requirements || '',
      status: entry.status || '未准备',
      files: entry.files || []
    }
  }
  return {
    common_files: prep.common_files,
    participants
  }
}

function formatSize(size) {
  const value = Number(size || 0)
  if (value >= 1024 * 1024) return `${(value / 1024 / 1024).toFixed(1)} MB`
  if (value >= 1024) return `${(value / 1024).toFixed(1)} KB`
  return `${value} B`
}

async function savePreparation() {
  if (!props.meeting?.id) return
  saving.value = true
  try {
    const data = await meetingsApi.updatePreparation(props.meeting.id, buildPayload())
    applyPreparation(data)
    ElMessage.success('会前准备已保存')
  } finally {
    saving.value = false
  }
}

async function uploadFile(file, scope, personId = '') {
  if (!props.meeting?.id || !file?.raw) return
  const formData = new FormData()
  formData.append('scope', scope)
  formData.append('person_id', personId)
  formData.append('file', file.raw)
  loading.value = true
  try {
    const data = await meetingsApi.uploadPreparationFile(props.meeting.id, formData)
    applyPreparation(data)
    ElMessage.success('文件已上传')
  } finally {
    loading.value = false
  }
}

async function removeFile(file) {
  if (!props.meeting?.id || !file?.id) return
  try {
    await ElMessageBox.confirm(`确认删除文件“${file.name}”？`, '删除准备文件', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消'
    })
  } catch (e) {
    return
  }
  loading.value = true
  try {
    const data = await meetingsApi.deletePreparationFile(props.meeting.id, file.id)
    applyPreparation(data)
    ElMessage.success('文件已删除')
  } finally {
    loading.value = false
  }
}

</script>

<style scoped>
.prep-body {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.prep-section {
  padding: 16px;
  border: 1px solid #d2e0eb;
  border-radius: var(--radius);
  background: #ffffff;
}

.section-head,
.person-head,
.file-toolbar,
.prep-file {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.section-head {
  margin-bottom: 14px;
}

.section-head h3 {
  margin: 0;
  color: #071a33;
  font-size: 16px;
  font-weight: 900;
}

.section-head p,
.person-head span,
.file-toolbar,
.empty-files,
.prep-file span {
  margin: 4px 0 0;
  color: var(--color-text-muted);
  font-size: 12px;
}

.participant-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.participant-card {
  padding: 14px;
  border: 1px solid #dbe8f1;
  border-radius: var(--radius);
  background: #f8fbfd;
}

.person-head {
  margin-bottom: 10px;
}

.person-head strong {
  display: block;
  color: #071a33;
  font-size: 15px;
}

.file-toolbar {
  margin: 12px 0 8px;
}

.prep-files {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.prep-file {
  min-height: 34px;
  padding: 6px 10px;
  border: 1px solid #e1ebf2;
  border-radius: 7px;
  background: #ffffff;
}

.prep-file a {
  flex: 1;
  min-width: 0;
  color: var(--color-primary);
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 760px) {
  :deep(.el-drawer) {
    width: 100% !important;
  }

  .section-head,
  .person-head,
  .file-toolbar,
  .prep-file {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
