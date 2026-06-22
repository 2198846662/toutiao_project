import axios from 'axios'
import { apiConfig } from '../config/api'

const adminBase = `${apiConfig.baseURL}/api/admin`

const authHeaders = (token) => ({
  Authorization: token ? `Bearer ${token}` : '',
})

export const adminApi = {
  getDashboard(token) {
    return axios.get(`${adminBase}/dashboard`, { headers: authHeaders(token) })
  },

  getNewsList(token, params) {
    return axios.get(`${adminBase}/news/list`, { headers: authHeaders(token), params })
  },

  addNews(token, data) {
    return axios.post(`${adminBase}/news/add`, data, { headers: authHeaders(token) })
  },

  updateNews(token, id, data) {
    return axios.put(`${adminBase}/news/update/${id}`, data, { headers: authHeaders(token) })
  },

  deleteNews(token, id) {
    return axios.delete(`${adminBase}/news/delete/${id}`, { headers: authHeaders(token) })
  },

  getCategories(token) {
    return axios.get(`${adminBase}/category/list`, { headers: authHeaders(token) })
  },

  addCategory(token, data) {
    return axios.post(`${adminBase}/category/add`, data, { headers: authHeaders(token) })
  },

  updateCategory(token, id, data) {
    return axios.put(`${adminBase}/category/update/${id}`, data, { headers: authHeaders(token) })
  },

  deleteCategory(token, id) {
    return axios.delete(`${adminBase}/category/delete/${id}`, { headers: authHeaders(token) })
  },

  getUsers(token, params) {
    return axios.get(`${adminBase}/users/list`, { headers: authHeaders(token), params })
  },
}
