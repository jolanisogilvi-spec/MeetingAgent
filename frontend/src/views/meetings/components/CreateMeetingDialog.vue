<template>
  <el-dialog
    :model-value="modelValue"
    :title="isEdit ? '编辑会议信息' : '新建会议'"
    width="640px"
    :close-on-click-modal="false"
    @update:model-value="$emit('update:modelValue', $event)"
    @open="onOpen"
    @closed="resetForm"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      label-position="right"
    >
      <el-form-item label="会议名称" prop="title">
        <el-input v-model="form.title" maxlength="255" placeholder="例如：项目周会" />
      </el-form-item>
      <el-form-item label="会议时间" prop="meeting_time">
        <el-date-picker
          v-model="form.meeting_time"
          type="datetime"
          placeholder="可选"
          value-format="YYYY-MM-DDTHH:mm:ss"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="所属部门" prop="department_id">
        <el-select
          v-model="form.department_id"
          placeholder="可选"
          clearable
          filterable
          style="width: 100%"
        >
          <el-option
            v-for="d in departments"
            :key="d.id"
            :label="d.name"
            :value="d.id"
          />
        </el-select>
      </el-form-item>
      <el-form-item label="参会人员" prop="participant_ids">
        <el-select
          v-model="form.participant_ids"
          multiple
          filterable
          collapse-tags
          collapse-tags-tooltip
          placeholder="可多选；默认按部门过滤"
          style="width: 100%"
        >
          <el-option
            v-for="p in filteredPeople"
            :key="p.id"
            :label="`${p.name}${p.role ? ' · ' + p.role : ''}`"
            :value="p.id"
          />
        </el-select>
        <div class="hint">
          <el-checkbox v-model="showAllPeople">显示全部人员（不按所属部门过滤）</el-checkbox>
        </div>
      </el-form-item>
      <el-form-item label="会议类型" prop="meeting_type">
        <el-input v-model="form.meeting_type" placeholder="例如：周会 / 评审会 / 决策会" />
      </el-form-item>
      <el-form-item label="会议目标" prop="objective">
        <el-input v-model="form.objective" type="textarea" :rows="2" placeholder="可选" />
      </el-form-item>
      <el-form-item label="备注" prop="notes">
        <el-input v-model="form.notes" type="textarea" :rows="2" placeholder="可选" />
      </el-form-item>
    </el-form>
    <template #footer>
      <el-button @click="onClose">取消</el-button>
      <el-button type="primary" :loading="submitting" @click="onSubmit">
        {{ isEdit ? '保存' : '创建' }}
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { computed, reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { meetingsApi } from '@/api'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  departments: { type: Array, default: () => [] },
  people: { type: Array, default: () => [] },
  meeting: { type: Object, default: null }
})
const emit = defineEmits(['update:modelValue', 'created', 'updated'])

const isEdit = computed(() => Boolean(props.meeting?.id))

const formRef = ref(null)
const submitting = ref(false)
const showAllPeople = ref(false)

const form = reactive({
  title: '',
  meeting_time: '',
  department_id: '',
  participant_ids: [],
  meeting_type: '',
  objective: '',
  notes: ''
})

const rules = {
  title: [{ required: true, message: '请输入会议名称', trigger: 'blur' }]
}

const filteredPeople = computed(() => {
  if (showAllPeople.value || !form.department_id) return props.people
  return props.people.filter((p) => p.department_id === form.department_id)
})

watch(
  () => form.department_id,
  (deptId, oldId) => {
    if (oldId === undefined) return
    if (!deptId || showAllPeople.value) return
    form.participant_ids = form.participant_ids.filter((id) => {
      const person = props.people.find((p) => p.id === id)
      return person && person.department_id === deptId
    })
  }
)

function onOpen() {
  if (isEdit.value) {
    const m = props.meeting
    form.title = m.title || ''
    form.meeting_time = m.meeting_time || ''
    form.department_id = m.department_id || ''
    form.participant_ids = [...(m.participant_ids || [])]
    form.meeting_type = m.meeting_type || ''
    form.objective = m.objective || ''
    form.notes = m.notes || ''
    showAllPeople.value = true
  } else {
    resetForm()
  }
}

function resetForm() {
  form.title = ''
  form.meeting_time = ''
  form.department_id = ''
  form.participant_ids = []
  form.meeting_type = ''
  form.objective = ''
  form.notes = ''
  showAllPeople.value = false
  formRef.value?.clearValidate()
}

function onClose() {
  emit('update:modelValue', false)
}

async function onSubmit() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload = {
      title: form.title,
      meeting_time: form.meeting_time || '',
      department_id: form.department_id || '',
      participant_ids: [...form.participant_ids],
      meeting_type: form.meeting_type || '',
      objective: form.objective || '',
      notes: form.notes || ''
    }
    if (isEdit.value) {
      const updated = await meetingsApi.update(props.meeting.id, payload)
      ElMessage.success('会议信息已保存')
      emit('updated', updated)
    } else {
      const meeting = await meetingsApi.create(payload)
      ElMessage.success('会议已创建')
      emit('created', meeting)
    }
    emit('update:modelValue', false)
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.hint {
  margin-top: 4px;
  font-size: 12px;
  color: var(--color-text-muted);
}
</style>
