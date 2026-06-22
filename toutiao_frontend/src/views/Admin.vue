<template>
  <div class="admin-page">
    <aside class="admin-sidebar">
      <div class="brand">
        <div class="brand-mark">T</div>
        <div>
          <strong>头条后台</strong>
          <span>内容管理</span>
        </div>
      </div>

      <button
        v-for="item in navItems"
        :key="item.key"
        :class="['nav-item', { active: activeSection === item.key }]"
        type="button"
        @click="activeSection = item.key"
      >
        <van-icon :name="item.icon" />
        <span>{{ item.label }}</span>
      </button>
    </aside>

    <main class="admin-main">
      <header class="admin-header">
        <div>
          <h1>{{ currentTitle }}</h1>
          <p>{{ currentSubtitle }}</p>
        </div>
        <div class="admin-user">
          <span>{{ userStore.userInfo?.username || '未登录' }}</span>
          <button type="button" @click="goHome">返回前台</button>
        </div>
      </header>

      <section v-if="status === 'login'" class="state-panel">
        <h2>需要登录</h2>
        <p>请先登录管理员账号。</p>
        <van-button type="primary" @click="router.push('/login')">去登录</van-button>
      </section>

      <section v-else-if="status === 'forbidden'" class="state-panel">
        <h2>无管理员权限</h2>
        <p>当前账号不能访问后台管理。</p>
        <van-button plain type="primary" @click="goHome">返回首页</van-button>
      </section>

      <section v-else-if="status === 'error'" class="state-panel">
        <h2>加载失败</h2>
        <p>{{ errorText }}</p>
        <van-button type="primary" @click="bootstrap">重试</van-button>
      </section>

      <template v-else>
        <section v-if="activeSection === 'dashboard'" class="section-body">
          <div class="metric-grid">
            <div v-for="metric in metrics" :key="metric.key" class="metric-card">
              <span>{{ metric.label }}</span>
              <strong>{{ dashboard[metric.key] ?? 0 }}</strong>
            </div>
          </div>
        </section>

        <section v-if="activeSection === 'news'" class="section-body">
          <div class="toolbar">
            <input v-model.trim="newsQuery.keyword" placeholder="搜索标题、作者" @keyup.enter="loadNews" />
            <select v-model.number="newsQuery.categoryId">
              <option :value="0">全部分类</option>
              <option v-for="item in categories" :key="item.id" :value="item.id">{{ item.name }}</option>
            </select>
            <van-button type="primary" @click="loadNews">查询</van-button>
            <van-button type="success" @click="openNewsForm()">新增新闻</van-button>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>标题</th>
                  <th>分类</th>
                  <th>作者</th>
                  <th>浏览</th>
                  <th>发布时间</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in newsRows" :key="item.id">
                  <td>{{ item.id }}</td>
                  <td class="title-cell">{{ item.title }}</td>
                  <td>{{ categoryName(item.categoryId) }}</td>
                  <td>{{ item.author || '-' }}</td>
                  <td>{{ item.views }}</td>
                  <td>{{ formatTime(item.publishTime) }}</td>
                  <td>
                    <button class="link-btn" type="button" @click="openNewsForm(item)">编辑</button>
                    <button class="danger-btn" type="button" @click="removeNews(item)">删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
            <van-empty v-if="!newsRows.length" description="暂无新闻" />
          </div>

          <div class="pager">
            <van-button size="small" :disabled="newsQuery.page <= 1" @click="changeNewsPage(-1)">上一页</van-button>
            <span>第 {{ newsQuery.page }} 页 / 共 {{ newsTotal }} 条</span>
            <van-button size="small" :disabled="newsQuery.page * newsQuery.pageSize >= newsTotal" @click="changeNewsPage(1)">
              下一页
            </van-button>
          </div>
        </section>

        <section v-if="activeSection === 'categories'" class="section-body">
          <div class="toolbar">
            <input v-model.trim="categoryForm.name" placeholder="分类名称" />
            <input v-model.number="categoryForm.sortOrder" type="number" placeholder="排序" />
            <van-button type="primary" @click="saveCategory">{{ categoryForm.id ? '保存分类' : '新增分类' }}</van-button>
            <van-button v-if="categoryForm.id" plain @click="resetCategoryForm">取消</van-button>
          </div>

          <div class="table-wrap compact">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>分类名称</th>
                  <th>排序</th>
                  <th>操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in categories" :key="item.id">
                  <td>{{ item.id }}</td>
                  <td>{{ item.name }}</td>
                  <td>{{ item.sortOrder }}</td>
                  <td>
                    <button class="link-btn" type="button" @click="editCategory(item)">编辑</button>
                    <button class="danger-btn" type="button" @click="removeCategory(item)">删除</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="activeSection === 'users'" class="section-body">
          <div class="toolbar">
            <input v-model.trim="userQuery.keyword" placeholder="搜索用户名、昵称、手机号" @keyup.enter="loadUsers" />
            <van-button type="primary" @click="loadUsers">查询</van-button>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>用户名</th>
                  <th>昵称</th>
                  <th>手机号</th>
                  <th>角色</th>
                  <th>注册时间</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in userRows" :key="item.id">
                  <td>{{ item.id }}</td>
                  <td>{{ item.username }}</td>
                  <td>{{ item.nickname || '-' }}</td>
                  <td>{{ item.phone || '-' }}</td>
                  <td><span :class="['role-pill', item.role]">{{ item.role }}</span></td>
                  <td>{{ formatTime(item.createdAt) }}</td>
                </tr>
              </tbody>
            </table>
            <van-empty v-if="!userRows.length" description="暂无用户" />
          </div>

          <div class="pager">
            <van-button size="small" :disabled="userQuery.page <= 1" @click="changeUserPage(-1)">上一页</van-button>
            <span>第 {{ userQuery.page }} 页 / 共 {{ userTotal }} 条</span>
            <van-button size="small" :disabled="userQuery.page * userQuery.pageSize >= userTotal" @click="changeUserPage(1)">
              下一页
            </van-button>
          </div>
        </section>
      </template>
    </main>

    <van-popup v-model:show="showNewsPopup" position="right" :style="{ width: 'min(680px, 92vw)', height: '100%' }">
      <div class="drawer">
        <header>
          <h2>{{ newsForm.id ? '编辑新闻' : '新增新闻' }}</h2>
          <button type="button" @click="showNewsPopup = false">关闭</button>
        </header>

        <label>
          标题
          <input v-model.trim="newsForm.title" />
        </label>
        <label>
          简介
          <textarea v-model.trim="newsForm.description" rows="2" />
        </label>
        <label>
          正文
          <textarea v-model.trim="newsForm.content" rows="8" />
        </label>
        <label>
          图片地址
          <input v-model.trim="newsForm.image" />
        </label>
        <div class="form-grid">
          <label>
            作者
            <input v-model.trim="newsForm.author" />
          </label>
          <label>
            分类
            <select v-model.number="newsForm.categoryId">
              <option v-for="item in categories" :key="item.id" :value="item.id">{{ item.name }}</option>
            </select>
          </label>
          <label>
            浏览量
            <input v-model.number="newsForm.views" type="number" min="0" />
          </label>
          <label>
            发布时间
            <input v-model="newsForm.publishTime" type="datetime-local" />
          </label>
        </div>

        <footer>
          <van-button plain @click="showNewsPopup = false">取消</van-button>
          <van-button type="primary" :loading="saving" @click="saveNews">保存</van-button>
        </footer>
      </div>
    </van-popup>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { showConfirmDialog, showFailToast, showSuccessToast } from 'vant'
import { adminApi } from '../api/admin'
import { useUserStore } from '../store/user'

const router = useRouter()
const userStore = useUserStore()

const navItems = [
  { key: 'dashboard', label: '概览', icon: 'bar-chart-o', subtitle: '核心数据与运营状态' },
  { key: 'news', label: '新闻', icon: 'newspaper-o', subtitle: '维护新闻内容与发布信息' },
  { key: 'categories', label: '分类', icon: 'apps-o', subtitle: '管理新闻频道和排序' },
  { key: 'users', label: '用户', icon: 'friends-o', subtitle: '查看注册用户和角色' },
]

const metrics = [
  { key: 'newsCount', label: '新闻数' },
  { key: 'categoryCount', label: '分类数' },
  { key: 'userCount', label: '用户数' },
  { key: 'favoriteCount', label: '收藏数' },
  { key: 'historyCount', label: '浏览记录' },
]

const activeSection = ref('dashboard')
const status = ref('loading')
const errorText = ref('')
const saving = ref(false)
const showNewsPopup = ref(false)

const dashboard = reactive({})
const categories = ref([])
const newsRows = ref([])
const newsTotal = ref(0)
const userRows = ref([])
const userTotal = ref(0)

const newsQuery = reactive({ page: 1, pageSize: 10, keyword: '', categoryId: 0 })
const userQuery = reactive({ page: 1, pageSize: 10, keyword: '' })
const categoryForm = reactive({ id: null, name: '', sortOrder: 0 })
const newsForm = reactive(createEmptyNewsForm())

const currentNav = computed(() => navItems.find((item) => item.key === activeSection.value) || navItems[0])
const currentTitle = computed(() => currentNav.value.label)
const currentSubtitle = computed(() => currentNav.value.subtitle)

function createEmptyNewsForm() {
  return {
    id: null,
    title: '',
    description: '',
    content: '',
    image: '',
    author: '',
    categoryId: 1,
    views: 0,
    publishTime: '',
  }
}

function token() {
  return userStore.token || ''
}

function normalizeError(error) {
  return error?.response?.data?.message || error?.response?.data?.detail || error?.message || '操作失败'
}

function formatTime(value) {
  if (!value) return '-'
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return '-'
  const y = date.getFullYear()
  const m = `${date.getMonth() + 1}`.padStart(2, '0')
  const d = `${date.getDate()}`.padStart(2, '0')
  const h = `${date.getHours()}`.padStart(2, '0')
  const min = `${date.getMinutes()}`.padStart(2, '0')
  return `${y}-${m}-${d} ${h}:${min}`
}

function toDateTimeInput(value) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return ''
  const y = date.getFullYear()
  const m = `${date.getMonth() + 1}`.padStart(2, '0')
  const d = `${date.getDate()}`.padStart(2, '0')
  const h = `${date.getHours()}`.padStart(2, '0')
  const min = `${date.getMinutes()}`.padStart(2, '0')
  return `${y}-${m}-${d}T${h}:${min}`
}

function categoryName(id) {
  return categories.value.find((item) => item.id === id)?.name || '未分类'
}

function goHome() {
  router.push('/home')
}

async function bootstrap() {
  if (!token()) {
    status.value = 'login'
    return
  }

  status.value = 'loading'
  try {
    await Promise.all([loadDashboard(), loadCategories(), loadNews(), loadUsers()])
    status.value = 'ready'
  } catch (error) {
    if (error?.response?.status === 403) {
      status.value = 'forbidden'
      return
    }
    errorText.value = normalizeError(error)
    status.value = 'error'
  }
}

async function loadDashboard() {
  const response = await adminApi.getDashboard(token())
  Object.assign(dashboard, response.data?.data || {})
}

async function loadCategories() {
  const response = await adminApi.getCategories(token())
  categories.value = response.data?.data || []
  if (!newsForm.categoryId && categories.value.length) {
    newsForm.categoryId = categories.value[0].id
  }
}

async function loadNews() {
  const response = await adminApi.getNewsList(token(), {
    page: newsQuery.page,
    pageSize: newsQuery.pageSize,
    keyword: newsQuery.keyword || undefined,
    categoryId: newsQuery.categoryId || undefined,
  })
  newsRows.value = response.data?.data?.list || []
  newsTotal.value = response.data?.data?.total || 0
}

async function loadUsers() {
  const response = await adminApi.getUsers(token(), {
    page: userQuery.page,
    pageSize: userQuery.pageSize,
    keyword: userQuery.keyword || undefined,
  })
  userRows.value = response.data?.data?.list || []
  userTotal.value = response.data?.data?.total || 0
}

function changeNewsPage(delta) {
  newsQuery.page += delta
  loadNews().catch((error) => showFailToast(normalizeError(error)))
}

function changeUserPage(delta) {
  userQuery.page += delta
  loadUsers().catch((error) => showFailToast(normalizeError(error)))
}

function openNewsForm(row = null) {
  Object.assign(newsForm, createEmptyNewsForm())
  if (categories.value.length) {
    newsForm.categoryId = categories.value[0].id
  }
  if (row) {
    Object.assign(newsForm, {
      ...row,
      publishTime: toDateTimeInput(row.publishTime),
    })
  }
  showNewsPopup.value = true
}

async function saveNews() {
  if (!newsForm.title || !newsForm.content || !newsForm.categoryId) {
    showFailToast('请填写标题、正文和分类')
    return
  }

  saving.value = true
  const payload = {
    title: newsForm.title,
    description: newsForm.description || null,
    content: newsForm.content,
    image: newsForm.image || null,
    author: newsForm.author || null,
    categoryId: newsForm.categoryId,
    views: Number(newsForm.views) || 0,
    publishTime: newsForm.publishTime ? new Date(newsForm.publishTime).toISOString() : null,
  }

  try {
    if (newsForm.id) {
      await adminApi.updateNews(token(), newsForm.id, payload)
    } else {
      await adminApi.addNews(token(), payload)
    }
    showSuccessToast('保存成功')
    showNewsPopup.value = false
    await Promise.all([loadNews(), loadDashboard()])
  } catch (error) {
    showFailToast(normalizeError(error))
  } finally {
    saving.value = false
  }
}

async function removeNews(row) {
  try {
    await showConfirmDialog({ title: '删除新闻', message: `确认删除「${row.title}」？` })
    await adminApi.deleteNews(token(), row.id)
    showSuccessToast('删除成功')
    await Promise.all([loadNews(), loadDashboard()])
  } catch (error) {
    if (error !== 'cancel') showFailToast(normalizeError(error))
  }
}

function editCategory(row) {
  Object.assign(categoryForm, {
    id: row.id,
    name: row.name,
    sortOrder: row.sortOrder,
  })
}

function resetCategoryForm() {
  Object.assign(categoryForm, { id: null, name: '', sortOrder: 0 })
}

async function saveCategory() {
  if (!categoryForm.name) {
    showFailToast('请填写分类名称')
    return
  }

  const payload = {
    name: categoryForm.name,
    sortOrder: Number(categoryForm.sortOrder) || 0,
  }

  try {
    if (categoryForm.id) {
      await adminApi.updateCategory(token(), categoryForm.id, payload)
    } else {
      await adminApi.addCategory(token(), payload)
    }
    showSuccessToast('保存成功')
    resetCategoryForm()
    await Promise.all([loadCategories(), loadDashboard()])
  } catch (error) {
    showFailToast(normalizeError(error))
  }
}

async function removeCategory(row) {
  try {
    await showConfirmDialog({ title: '删除分类', message: `确认删除「${row.name}」？` })
    await adminApi.deleteCategory(token(), row.id)
    showSuccessToast('删除成功')
    await Promise.all([loadCategories(), loadDashboard()])
  } catch (error) {
    if (error !== 'cancel') showFailToast(normalizeError(error))
  }
}

watch(
  () => [newsQuery.keyword, newsQuery.categoryId],
  () => {
    newsQuery.page = 1
  }
)

onMounted(bootstrap)
</script>

<style scoped>
.admin-page {
  min-height: 100vh;
  display: grid;
  grid-template-columns: 232px minmax(0, 1fr);
  background: #eef1f4;
  color: #20242a;
}

.admin-sidebar {
  background: #15191f;
  color: #f7f9fb;
  padding: 20px 14px;
}

.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 4px 6px 22px;
}

.brand-mark {
  width: 38px;
  height: 38px;
  display: grid;
  place-items: center;
  background: #0ea5a4;
  color: #fff;
  font-weight: 800;
  border-radius: 6px;
}

.brand strong,
.brand span {
  display: block;
}

.brand span {
  color: #aab3bf;
  font-size: 12px;
  margin-top: 2px;
}

.nav-item {
  width: 100%;
  height: 42px;
  display: flex;
  align-items: center;
  gap: 10px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: #c7d0db;
  padding: 0 12px;
  margin-bottom: 6px;
  cursor: pointer;
  text-align: left;
}

.nav-item.active,
.nav-item:hover {
  background: #242b34;
  color: #fff;
}

.admin-main {
  min-width: 0;
  padding: 22px;
}

.admin-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 18px;
}

.admin-header h1 {
  margin: 0;
  font-size: 24px;
}

.admin-header p {
  margin: 5px 0 0;
  color: #697386;
}

.admin-user {
  display: flex;
  align-items: center;
  gap: 12px;
  color: #4c5768;
}

.admin-user button,
.link-btn,
.danger-btn,
.drawer header button {
  border: 0;
  background: transparent;
  cursor: pointer;
}

.admin-user button {
  height: 34px;
  padding: 0 12px;
  border-radius: 6px;
  color: #0969da;
  background: #fff;
}

.section-body,
.state-panel {
  background: #fff;
  border: 1px solid #dde3ea;
  border-radius: 8px;
  padding: 18px;
}

.state-panel {
  max-width: 520px;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(120px, 1fr));
  gap: 14px;
}

.metric-card {
  border: 1px solid #e0e5eb;
  border-radius: 8px;
  padding: 18px;
  background: #fbfcfd;
}

.metric-card span {
  display: block;
  color: #687385;
  font-size: 13px;
}

.metric-card strong {
  display: block;
  margin-top: 10px;
  font-size: 28px;
}

.toolbar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
  margin-bottom: 14px;
}

input,
select,
textarea {
  border: 1px solid #cfd7e2;
  border-radius: 6px;
  padding: 9px 10px;
  background: #fff;
  color: #20242a;
  outline: none;
}

input:focus,
select:focus,
textarea:focus {
  border-color: #0ea5a4;
  box-shadow: 0 0 0 3px rgba(14, 165, 164, 0.12);
}

.toolbar input {
  min-width: 220px;
}

.table-wrap {
  overflow-x: auto;
  border: 1px solid #e1e6ed;
  border-radius: 8px;
}

.table-wrap.compact {
  max-width: 760px;
}

table {
  width: 100%;
  border-collapse: collapse;
  background: #fff;
}

th,
td {
  padding: 12px;
  border-bottom: 1px solid #eef1f4;
  text-align: left;
  white-space: nowrap;
}

th {
  color: #5c6677;
  font-size: 13px;
  background: #f7f9fb;
}

.title-cell {
  min-width: 260px;
  max-width: 420px;
  white-space: normal;
}

.link-btn {
  color: #0969da;
  margin-right: 10px;
}

.danger-btn {
  color: #c2410c;
}

.pager {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 14px;
  color: #697386;
}

.role-pill {
  display: inline-flex;
  align-items: center;
  min-width: 58px;
  justify-content: center;
  height: 24px;
  border-radius: 999px;
  background: #edf2f7;
  color: #475569;
  font-size: 12px;
}

.role-pill.admin {
  background: #dcfce7;
  color: #15803d;
}

.drawer {
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 14px;
  padding: 18px;
  background: #fff;
  overflow-y: auto;
}

.drawer header,
.drawer footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.drawer h2 {
  margin: 0;
  font-size: 20px;
}

.drawer label {
  display: grid;
  gap: 6px;
  color: #4c5768;
  font-size: 13px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.drawer footer {
  justify-content: flex-end;
  gap: 10px;
  margin-top: auto;
  padding-top: 10px;
}

@media (max-width: 760px) {
  .admin-page {
    grid-template-columns: 1fr;
  }

  .admin-sidebar {
    position: sticky;
    top: 0;
    z-index: 2;
    display: flex;
    gap: 6px;
    overflow-x: auto;
    padding: 10px;
  }

  .brand {
    display: none;
  }

  .nav-item {
    width: auto;
    min-width: 86px;
    margin: 0;
  }

  .admin-main {
    padding: 14px;
  }

  .admin-header {
    align-items: flex-start;
    gap: 12px;
    flex-direction: column;
  }

  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}
</style>
