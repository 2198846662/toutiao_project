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
    return axios.get(`${adminBase}/news`, { headers: authHeaders(token), params })
  },

  addNews(token, data) {
    return axios.post(`${adminBase}/news`, data, { headers: authHeaders(token) })
  },

  updateNews(token, id, data) {
    return axios.put(`${adminBase}/news/${id}`, data, { headers: authHeaders(token) })
  },

  deleteNews(token, id) {
    return axios.delete(`${adminBase}/news/${id}`, { headers: authHeaders(token) })
  },

  getCategories(token) {
    return axios.get(`${adminBase}/categories`, { headers: authHeaders(token) })
  },

  addCategory(token, data) {
    return axios.post(`${adminBase}/categories`, data, { headers: authHeaders(token) })
  },

  updateCategory(token, id, data) {
    return axios.put(`${adminBase}/categories/${id}`, data, { headers: authHeaders(token) })
  },

  deleteCategory(token, id) {
    return axios.delete(`${adminBase}/categories/${id}`, { headers: authHeaders(token) })
  },

  getUsers(token, params) {
    return axios.get(`${adminBase}/users`, { headers: authHeaders(token), params })
  },
}
