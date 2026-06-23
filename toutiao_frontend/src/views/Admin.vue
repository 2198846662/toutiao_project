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
        :aria-current="activeSection === item.key ? 'page' : undefined"
        @click="activeSection = item.key"
      >
        <van-icon :name="item.icon" class="nav-icon" />
        <span class="nav-label">{{ item.label }}</span>
      </button>
    </aside>

    <main class="admin-main">
      <header class="admin-header">
        <div>
          <span class="eyebrow">Admin Console</span>
          <h1>{{ currentTitle }}</h1>
          <p>{{ currentSubtitle }}</p>
        </div>
        <div class="admin-user">
          <span class="online-dot"></span>
          <span>{{ userStore.userInfo?.username || '未登录' }}</span>
          <button type="button" @click="goHome">
            <van-icon name="wap-home-o" />
            返回前台
          </button>
        </div>
      </header>

      <section v-if="status === 'login'" class="state-panel">
        <h2>需要登录</h2>
        <p>请先登录管理员账号。</p>
        <van-button icon="user-o" type="primary" @click="router.push('/login')">去登录</van-button>
      </section>

      <section v-else-if="status === 'forbidden'" class="state-panel">
        <h2>无管理员权限</h2>
        <p>当前账号不能访问后台管理。</p>
        <van-button icon="wap-home-o" plain type="primary" @click="goHome">返回首页</van-button>
      </section>

      <section v-else-if="status === 'error'" class="state-panel">
        <h2>加载失败</h2>
        <p>{{ errorText }}</p>
        <van-button icon="replay" type="primary" @click="bootstrap">重试</van-button>
      </section>

      <template v-else>
        <section v-if="activeSection === 'dashboard'" class="section-body">
          <div class="section-heading">
            <div>
              <h2>运营概览</h2>
              <p>实时查看内容、用户和互动数据。</p>
            </div>
          </div>
          <div class="metric-grid">
            <div v-for="metric in metrics" :key="metric.key" class="metric-card">
              <div class="metric-icon">
                <van-icon :name="metric.icon" />
              </div>
              <span>{{ metric.label }}</span>
              <strong>{{ dashboard[metric.key] ?? 0 }}</strong>
              <small>{{ metric.hint }}</small>
            </div>
          </div>
        </section>

        <section v-if="activeSection === 'news'" class="section-body">
          <div class="section-heading">
            <div>
              <h2>新闻管理</h2>
              <p>筛选、编辑和发布新闻内容。</p>
            </div>
            <span class="count-chip">{{ newsTotal }} 条新闻</span>
          </div>
          <div class="toolbar">
            <label class="field-control">
              <span>关键词</span>
              <input v-model.trim="newsQuery.keyword" placeholder="搜索标题、作者" @keyup.enter="loadNews" />
            </label>
            <label class="field-control">
              <span>分类</span>
              <select v-model.number="newsQuery.categoryId">
              <option :value="0">全部分类</option>
              <option v-for="item in categories" :key="item.id" :value="item.id">{{ item.name }}</option>
              </select>
            </label>
            <van-button icon="search" type="primary" @click="loadNews">查询</van-button>
            <van-button icon="plus" type="success" @click="openNewsForm()">新增新闻</van-button>
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
                  <th class="action-cell">操作</th>
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
                  <td class="action-cell">
                    <button class="link-btn" type="button" @click="openNewsForm(item)">
                      <van-icon name="edit" />
                      编辑
                    </button>
                    <button class="danger-btn" type="button" @click="removeNews(item)">
                      <van-icon name="delete-o" />
                      删除
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
            <van-empty v-if="!newsRows.length" description="暂无新闻" />
          </div>

          <div class="pager">
            <van-button icon="arrow-left" size="small" :disabled="newsQuery.page <= 1" @click="changeNewsPage(-1)">上一页</van-button>
            <span>第 {{ newsQuery.page }} 页 / 共 {{ newsTotal }} 条</span>
            <van-button icon="arrow" size="small" :disabled="newsQuery.page * newsQuery.pageSize >= newsTotal" @click="changeNewsPage(1)">
              下一页
            </van-button>
          </div>
        </section>

        <section v-if="activeSection === 'categories'" class="section-body">
          <div class="section-heading">
            <div>
              <h2>分类管理</h2>
              <p>维护频道名称和展示排序。</p>
            </div>
            <span class="count-chip">{{ categories.length }} 个分类</span>
          </div>
          <div class="toolbar">
            <label class="field-control">
              <span>分类名称</span>
              <input v-model.trim="categoryForm.name" placeholder="分类名称" />
            </label>
            <label class="field-control short">
              <span>排序</span>
              <input v-model.number="categoryForm.sortOrder" type="number" placeholder="排序" />
            </label>
            <van-button icon="plus" type="primary" @click="saveCategory">{{ categoryForm.id ? '保存分类' : '新增分类' }}</van-button>
            <van-button v-if="categoryForm.id" icon="cross" plain @click="resetCategoryForm">取消</van-button>
          </div>

          <div class="table-wrap compact">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>分类名称</th>
                  <th>排序</th>
                  <th class="action-cell">操作</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in categories" :key="item.id">
                  <td>{{ item.id }}</td>
                  <td>{{ item.name }}</td>
                  <td>{{ item.sortOrder }}</td>
                  <td class="action-cell">
                    <button class="link-btn" type="button" @click="editCategory(item)">
                      <van-icon name="edit" />
                      编辑
                    </button>
                    <button class="danger-btn" type="button" @click="removeCategory(item)">
                      <van-icon name="delete-o" />
                      删除
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="activeSection === 'users'" class="section-body">
          <div class="section-heading">
            <div>
              <h2>用户管理</h2>
              <p>查看注册用户、身份和账号信息。</p>
            </div>
            <span class="count-chip">{{ userTotal }} 位用户</span>
          </div>
          <div class="toolbar">
            <label class="field-control">
              <span>关键词</span>
              <input v-model.trim="userQuery.keyword" placeholder="搜索用户名、昵称、手机号" @keyup.enter="loadUsers" />
            </label>
            <van-button icon="search" type="primary" @click="loadUsers">查询</van-button>
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
            <van-button icon="arrow-left" size="small" :disabled="userQuery.page <= 1" @click="changeUserPage(-1)">上一页</van-button>
            <span>第 {{ userQuery.page }} 页 / 共 {{ userTotal }} 条</span>
            <van-button icon="arrow" size="small" :disabled="userQuery.page * userQuery.pageSize >= userTotal" @click="changeUserPage(1)">
              下一页
            </van-button>
          </div>
        </section>
      </template>
    </main>

    <van-popup v-model:show="showNewsPopup" position="right" :style="{ width: 'min(680px, 92vw)', height: '100%' }">
      <div class="drawer">
        <header>
          <div>
            <span class="eyebrow">News Editor</span>
            <h2>{{ newsForm.id ? '编辑新闻' : '新增新闻' }}</h2>
          </div>
          <button type="button" aria-label="关闭编辑面板" @click="showNewsPopup = false">
            <van-icon name="cross" />
          </button>
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
          <van-button icon="cross" plain @click="showNewsPopup = false">取消</van-button>
          <van-button icon="success" type="primary" :loading="saving" @click="saveNews">保存</van-button>
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
  { key: 'newsCount', label: '新闻数', icon: 'newspaper-o', hint: '已入库内容' },
  { key: 'categoryCount', label: '分类数', icon: 'apps-o', hint: '频道配置' },
  { key: 'userCount', label: '用户数', icon: 'friends-o', hint: '注册账号' },
  { key: 'favoriteCount', label: '收藏数', icon: 'star-o', hint: '用户收藏' },
  { key: 'historyCount', label: '浏览记录', icon: 'clock-o', hint: '阅读轨迹' },
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
  --admin-bg: #f3f5f8;
  --panel-bg: #ffffff;
  --panel-soft: #f8fafc;
  --sidebar-bg: #111827;
  --sidebar-line: rgba(255, 255, 255, 0.08);
  --text-main: #172033;
  --text-muted: #697586;
  --line: #e3e8ef;
  --primary: #0f766e;
  --primary-strong: #0b5f59;
  --accent: #c2410c;
  min-height: 100vh;
  display: grid;
  grid-template-columns: 248px minmax(0, 1fr);
  background:
    linear-gradient(180deg, rgba(15, 118, 110, 0.08), transparent 280px),
    var(--admin-bg);
  color: var(--text-main);
  font-family: "Microsoft YaHei", "PingFang SC", "Segoe UI", sans-serif;
}

.admin-sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  color: #f8fafc;
  padding: 22px 14px;
  background:
    linear-gradient(180deg, #111827 0%, #172033 56%, #0f172a 100%);
  border-right: 1px solid rgba(255, 255, 255, 0.08);
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 6px 8px 22px;
  margin-bottom: 10px;
  border-bottom: 1px solid var(--sidebar-line);
}

.brand-mark {
  width: 42px;
  height: 42px;
  display: grid;
  place-items: center;
  color: #fff;
  font-size: 18px;
  font-weight: 900;
  border-radius: 8px;
  background: linear-gradient(135deg, #0f766e, #2563eb);
  box-shadow: 0 12px 26px rgba(15, 118, 110, 0.28);
}

.brand strong,
.brand span {
  display: block;
}

.brand strong {
  font-size: 17px;
  letter-spacing: 0;
}

.brand span {
  color: #aeb8c7;
  font-size: 12px;
  margin-top: 3px;
}

.nav-item {
  position: relative;
  width: 100%;
  height: 44px;
  display: flex;
  align-items: center;
  gap: 11px;
  border: 0;
  border-radius: 8px;
  background: transparent;
  color: #c8d1df;
  padding: 0 13px;
  margin-bottom: 6px;
  cursor: pointer;
  text-align: left;
  transition: background 0.18s ease, color 0.18s ease, transform 0.18s ease;
}

.nav-item:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.08);
}

.nav-item.active {
  color: #fff;
  background: rgba(15, 118, 110, 0.28);
}

.nav-item.active::before {
  content: "";
  position: absolute;
  left: 0;
  width: 3px;
  height: 22px;
  border-radius: 999px;
  background: #2dd4bf;
}

.nav-icon {
  font-size: 18px;
}

.nav-label {
  font-size: 14px;
  font-weight: 600;
}

.admin-main {
  min-width: 0;
  padding: 28px;
}

.admin-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 22px;
}

.eyebrow {
  display: inline-flex;
  align-items: center;
  color: var(--primary);
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0;
  text-transform: uppercase;
}

.admin-header h1 {
  margin: 4px 0 0;
  font-size: 30px;
  line-height: 1.18;
  letter-spacing: 0;
}

.admin-header p {
  margin: 7px 0 0;
  color: var(--text-muted);
  font-size: 14px;
}

.admin-user {
  min-height: 42px;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 6px 6px 6px 14px;
  color: #4b5565;
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(226, 232, 240, 0.92);
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(15, 23, 42, 0.06);
}

.online-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #16a34a;
  box-shadow: 0 0 0 4px rgba(22, 163, 74, 0.12);
}

.admin-user button,
.link-btn,
.danger-btn,
.drawer header button {
  border: 0;
  background: transparent;
  cursor: pointer;
  font: inherit;
}

.admin-user button {
  height: 32px;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 12px;
  border-radius: 7px;
  color: #fff;
  background: var(--text-main);
}

.section-body,
.state-panel {
  background: rgba(255, 255, 255, 0.92);
  border: 1px solid rgba(226, 232, 240, 0.95);
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 18px 42px rgba(15, 23, 42, 0.07);
}

.state-panel {
  max-width: 520px;
}

.state-panel h2 {
  margin: 0 0 8px;
}

.state-panel p {
  margin: 0 0 16px;
  color: var(--text-muted);
}

.section-heading {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
  margin-bottom: 18px;
}

.section-heading h2 {
  margin: 0;
  font-size: 18px;
  line-height: 1.25;
}

.section-heading p {
  margin: 6px 0 0;
  color: var(--text-muted);
  font-size: 13px;
}

.count-chip {
  display: inline-flex;
  align-items: center;
  height: 30px;
  padding: 0 12px;
  border-radius: 999px;
  color: #0f766e;
  background: #ccfbf1;
  font-size: 13px;
  font-weight: 700;
  white-space: nowrap;
}

.metric-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(126px, 1fr));
  gap: 14px;
}

.metric-card {
  position: relative;
  min-height: 150px;
  border: 1px solid var(--line);
  border-radius: 8px;
  padding: 17px;
  overflow: hidden;
  background:
    linear-gradient(180deg, #fff, #f8fafc);
  box-shadow: 0 10px 26px rgba(15, 23, 42, 0.05);
}

.metric-card::after {
  content: "";
  position: absolute;
  inset: auto 0 0;
  height: 3px;
  background: linear-gradient(90deg, #0f766e, #2563eb, #c2410c);
}

.metric-icon {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  color: #0f766e;
  border-radius: 8px;
  background: #e6fffb;
  margin-bottom: 14px;
}

.metric-card span {
  display: block;
  color: var(--text-muted);
  font-size: 13px;
}

.metric-card strong {
  display: block;
  margin-top: 8px;
  font-size: 30px;
  line-height: 1;
}

.metric-card small {
  display: block;
  margin-top: 12px;
  color: #95a1b2;
  font-size: 12px;
}

.toolbar {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  align-items: center;
  padding: 12px;
  margin-bottom: 14px;
  border: 1px solid #e6ebf2;
  border-radius: 8px;
  background: var(--panel-soft);
}

input,
select,
textarea {
  min-height: 38px;
  border: 1px solid #cfd7e2;
  border-radius: 7px;
  padding: 9px 11px;
  background: #fff;
  color: var(--text-main);
  outline: none;
  transition: border-color 0.16s ease, box-shadow 0.16s ease;
}

textarea {
  resize: vertical;
  line-height: 1.6;
}

input:focus,
select:focus,
textarea:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.12);
}

.toolbar input {
  min-width: 230px;
}

.toolbar select {
  min-width: 132px;
}

.table-wrap {
  overflow-x: auto;
  border: 1px solid #e1e7ef;
  border-radius: 8px;
  background: #fff;
}

.table-wrap.compact {
  max-width: 800px;
}

table {
  width: 100%;
  border-collapse: separate;
  border-spacing: 0;
  background: #fff;
}

th,
td {
  padding: 13px 14px;
  border-bottom: 1px solid #edf1f6;
  text-align: left;
  white-space: nowrap;
  vertical-align: middle;
}

th {
  position: sticky;
  top: 0;
  z-index: 1;
  color: #5f6c7d;
  font-size: 12px;
  font-weight: 800;
  background: #f8fafc;
}

tbody tr {
  transition: background 0.16s ease;
}

tbody tr:hover {
  background: #f8fbfb;
}

tbody tr:last-child td {
  border-bottom: 0;
}

.title-cell {
  min-width: 280px;
  max-width: 460px;
  white-space: normal;
  font-weight: 700;
  color: #1f2937;
}

.action-cell {
  position: sticky;
  right: 0;
  min-width: 128px;
  background: #fff;
  box-shadow: -12px 0 18px rgba(15, 23, 42, 0.05);
  z-index: 1;
}

tbody tr:hover .action-cell {
  background: #f8fbfb;
}

th.action-cell {
  background: #f8fafc;
  z-index: 2;
}

.link-btn,
.danger-btn {
  height: 30px;
  display: inline-flex;
  align-items: center;
  gap: 5px;
  padding: 0 10px;
  border-radius: 7px;
  font-size: 13px;
  font-weight: 700;
}

.link-btn {
  color: #0b5f59;
  background: #e6fffb;
  margin-right: 8px;
}

.danger-btn {
  color: #b42318;
  background: #fff1f0;
}

.pager {
  display: flex;
  align-items: center;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 15px;
  color: var(--text-muted);
  font-size: 13px;
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
  font-weight: 800;
}

.role-pill.admin {
  background: #dcfce7;
  color: #15803d;
}

.drawer {
  min-height: 100%;
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 22px;
  background: #f7f9fc;
  overflow-y: auto;
}

.drawer header,
.drawer footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.drawer header {
  padding-bottom: 14px;
  border-bottom: 1px solid #e3e8ef;
}

.drawer h2 {
  margin: 4px 0 0;
  font-size: 22px;
}

.drawer header button {
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border-radius: 8px;
  color: #475569;
  background: #fff;
  border: 1px solid #e3e8ef;
}

.drawer label {
  display: grid;
  gap: 7px;
  color: #4c5768;
  font-size: 13px;
  font-weight: 700;
}

.drawer input,
.drawer select,
.drawer textarea {
  font-weight: 400;
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
  padding-top: 12px;
  border-top: 1px solid #e3e8ef;
}

:deep(.van-button) {
  border-radius: 7px;
  font-weight: 700;
}

:deep(.van-button--primary) {
  background: var(--primary);
  border-color: var(--primary);
}

:deep(.van-button--success) {
  background: #2563eb;
  border-color: #2563eb;
}

@media (max-width: 1080px) {
  .metric-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
}

@media (max-width: 760px) {
  .admin-page {
    grid-template-columns: 1fr;
  }

  .admin-sidebar {
    position: sticky;
    top: 0;
    z-index: 3;
    height: auto;
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
    min-width: 88px;
    margin: 0;
    justify-content: center;
  }

  .nav-item.active::before {
    display: none;
  }

  .admin-main {
    padding: 16px;
  }

  .admin-header {
    align-items: stretch;
    flex-direction: column;
  }

  .admin-user {
    justify-content: space-between;
  }

  .section-body,
  .state-panel {
    padding: 15px;
  }

  .section-heading {
    flex-direction: column;
  }

  .metric-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .toolbar input,
  .toolbar select {
    width: 100%;
    min-width: 0;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }
}

/* ui-ux-pro-max: restrained content-management admin polish */
.admin-page {
  --admin-bg: #f5f7fa;
  --surface: #ffffff;
  --surface-muted: #f8fafc;
  --sidebar-bg: #172033;
  --sidebar-hover: #233047;
  --text-main: #1f2937;
  --text-muted: #64748b;
  --text-subtle: #94a3b8;
  --line: #e2e8f0;
  --line-strong: #cbd5e1;
  --primary: #176b87;
  --primary-hover: #12546a;
  --primary-soft: #e8f4f7;
  --danger: #b42318;
  --danger-soft: #fff1f0;
  --success: #2563eb;
  --focus: rgba(23, 107, 135, 0.18);
  grid-template-columns: 240px minmax(0, 1fr);
  background: var(--admin-bg);
  color: var(--text-main);
}

.admin-sidebar {
  padding: 18px 12px;
  background: var(--sidebar-bg);
  border-right: 1px solid #111827;
}

.brand {
  padding: 6px 8px 18px;
  margin-bottom: 12px;
  border-bottom-color: rgba(255, 255, 255, 0.08);
}

.brand-mark {
  width: 38px;
  height: 38px;
  font-size: 16px;
  font-weight: 800;
  background: var(--primary);
  box-shadow: none;
}

.nav-item {
  min-height: 44px;
  height: auto;
  gap: 10px;
  color: #d6deea;
  padding: 0 12px;
  margin-bottom: 4px;
  transition: background 0.18s ease, color 0.18s ease;
}

.nav-item:hover {
  background: var(--sidebar-hover);
}

.nav-item.active {
  background: var(--primary);
}

.nav-item.active::before {
  height: 24px;
  background: #fff;
}

.admin-main {
  padding: 24px 28px 32px;
  width: 100%;
  max-width: 1440px;
  margin: 0 auto;
}

.admin-header {
  align-items: center;
  margin-bottom: 24px;
}

.admin-header h1 {
  font-size: 28px;
}

.admin-user {
  min-height: 44px;
  background: var(--surface);
  border-color: var(--line);
  box-shadow: none;
}

.admin-user button:hover {
  background: #0f172a;
}

.section-body {
  padding: 0;
  background: transparent;
  border: 0;
  border-radius: 0;
  box-shadow: none;
}

.state-panel {
  padding: 24px;
  background: var(--surface);
  border: 1px solid var(--line);
  box-shadow: none;
}

.section-heading {
  margin-bottom: 14px;
}

.section-heading h2 {
  font-size: 20px;
}

.count-chip {
  min-height: 30px;
  color: var(--primary);
  background: var(--primary-soft);
}

.metric-grid {
  gap: 12px;
}

.metric-card {
  min-height: 136px;
  padding: 16px;
  background: var(--surface);
  box-shadow: none;
}

.metric-card::after {
  display: none;
}

.metric-icon {
  width: 32px;
  height: 32px;
  color: var(--primary);
  background: var(--primary-soft);
  margin-bottom: 12px;
}

.metric-card strong {
  font-size: 28px;
}

.metric-card small {
  color: var(--text-subtle);
}

.toolbar {
  align-items: flex-end;
  border-color: var(--line);
  background: var(--surface);
}

.field-control {
  display: grid;
  gap: 6px;
  min-width: 230px;
}

.field-control.short {
  min-width: 120px;
}

.field-control span {
  color: #475569;
  font-size: 12px;
  font-weight: 700;
}

input,
select,
textarea {
  min-height: 40px;
  border-color: var(--line-strong);
}

input:focus,
select:focus,
textarea:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 3px var(--focus);
}

.table-wrap {
  border-color: var(--line);
  background: var(--surface);
  width: 100%;
}

th,
td {
  padding: 12px 14px;
  border-bottom-color: #edf2f7;
}

th {
  color: #475569;
  background: var(--surface-muted);
}

tbody tr:hover {
  background: #f8fafc;
}

.title-cell {
  font-weight: 600;
}

.action-cell {
  background: var(--surface);
  box-shadow: -10px 0 16px rgba(15, 23, 42, 0.04);
}

tbody tr:hover .action-cell {
  background: #f8fafc;
}

th.action-cell {
  background: var(--surface-muted);
}

.link-btn,
.danger-btn {
  min-height: 32px;
}

.link-btn {
  color: var(--primary);
  background: var(--primary-soft);
}

.link-btn:hover {
  color: #fff;
  background: var(--primary);
}

.danger-btn {
  color: var(--danger);
  background: var(--danger-soft);
}

.danger-btn:hover {
  color: #fff;
  background: var(--danger);
}

.drawer {
  background: var(--surface);
}

.drawer header button {
  min-width: 40px;
  min-height: 40px;
}

:deep(.van-button) {
  min-height: 40px;
}

:deep(.van-button--primary) {
  background: var(--primary);
  border-color: var(--primary);
}

:deep(.van-button--primary:hover) {
  background: var(--primary-hover);
  border-color: var(--primary-hover);
}

:deep(.van-button--success) {
  background: var(--success);
  border-color: var(--success);
}

button:focus-visible,
input:focus-visible,
select:focus-visible,
textarea:focus-visible,
:deep(.van-button:focus-visible) {
  outline: 2px solid var(--primary);
  outline-offset: 2px;
}

@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    transition: none !important;
  }
}

@media (max-width: 760px) {
  .admin-main {
    padding: 16px;
  }

  .admin-user {
    align-items: center;
  }

  .field-control,
  .field-control.short,
  .toolbar input,
  .toolbar select {
    width: 100%;
    min-width: 0;
  }

  .section-body {
    padding: 0;
  }
}
</style>
