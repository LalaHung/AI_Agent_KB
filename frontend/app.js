// API configuration
const API_URL = "https://script.google.com/macros/s/AKfycbyDDFd_zYk5gAL7V3ogF2NxwZSKeH1UdUP_nIXZWY99znWRyBbWV-uMW9RBm6uZuRTk/exec";

// App state
let state = {
  grades: [],
  filteredGrades: [],
  filters: {
    search: "",
    subject: "",
    status: ""
  },
  editingId: null
};

// DOM Elements
const elements = {
  themeToggle: document.getElementById("theme-toggle"),
  addRecordBtn: document.getElementById("add-record-btn"),
  recordModal: document.getElementById("record-modal"),
  closeModalBtn: document.getElementById("close-modal-btn"),
  cancelFormBtn: document.getElementById("cancel-form-btn"),
  recordForm: document.getElementById("record-form"),
  modalTitle: document.getElementById("modal-title"),
  
  // Form fields
  formId: document.getElementById("form-id"),
  formStudentId: document.getElementById("form-student-id"),
  formName: document.getElementById("form-name"),
  formSubject: document.getElementById("form-subject"),
  formScore: document.getElementById("form-score"),
  formDate: document.getElementById("form-date"),
  formRemarks: document.getElementById("form-remarks"),
  submitFormBtn: document.getElementById("submit-form-btn"),
  
  // Dashboard stats
  statTotal: document.getElementById("stat-total"),
  statAverage: document.getElementById("stat-average"),
  statPassRate: document.getElementById("stat-pass-rate"),
  statMinMax: document.getElementById("stat-minmax"),
  
  // Filters & Table
  searchInput: document.getElementById("search-input"),
  subjectFilter: document.getElementById("subject-filter"),
  statusFilter: document.getElementById("status-filter"),
  gradesTable: document.getElementById("grades-table"),
  gradesTbody: document.getElementById("grades-tbody"),
  
  // States
  loadingState: document.getElementById("loading-state"),
  emptyState: document.getElementById("empty-state"),
  
  // Toast
  toast: document.getElementById("toast"),
  toastMessage: document.getElementById("toast-message")
};

// Initialize Application
document.addEventListener("DOMContentLoaded", () => {
  initTheme();
  setupEventListeners();
  fetchGrades();
  
  // Set default date in form to today
  elements.formDate.value = new Date().toISOString().split('T')[0];
});

// Theme Management
function initTheme() {
  const savedTheme = localStorage.getItem("theme") || "light";
  document.documentElement.setAttribute("data-theme", savedTheme);
  updateThemeIcon(savedTheme);
}

function toggleTheme() {
  const currentTheme = document.documentElement.getAttribute("data-theme");
  const newTheme = currentTheme === "dark" ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", newTheme);
  localStorage.setItem("theme", newTheme);
  updateThemeIcon(newTheme);
}

function updateThemeIcon(theme) {
  const icon = elements.themeToggle.querySelector("i");
  if (theme === "dark") {
    icon.className = "fa-solid fa-sun";
  } else {
    icon.className = "fa-solid fa-moon";
  }
}

// Event Listeners
function setupEventListeners() {
  elements.themeToggle.addEventListener("click", toggleTheme);
  
  // Modal triggers
  elements.addRecordBtn.addEventListener("click", () => openModal());
  elements.closeModalBtn.addEventListener("click", closeModal);
  elements.cancelFormBtn.addEventListener("click", closeModal);
  elements.recordModal.addEventListener("click", (e) => {
    if (e.target === elements.recordModal) closeModal();
  });
  
  // Form submission
  elements.recordForm.addEventListener("submit", handleFormSubmit);
  
  // Search & Filters
  elements.searchInput.addEventListener("input", (e) => {
    state.filters.search = e.target.value.trim().toLowerCase();
    applyFilters();
  });
  
  elements.subjectFilter.addEventListener("change", (e) => {
    state.filters.subject = e.target.value;
    applyFilters();
  });
  
  elements.statusFilter.addEventListener("change", (e) => {
    state.filters.status = e.target.value;
    applyFilters();
  });
}

// Fetch Grades from Google Sheets API (via Web App redirect)
async function fetchGrades() {
  showLoading(true);
  try {
    const response = await fetch(API_URL);
    if (!response.ok) throw new Error("網路連線錯誤");
    const data = await response.json();
    
    if (Array.isArray(data)) {
      state.grades = data;
    } else {
      state.grades = [];
      showToast("載入資料失敗，傳回格式錯誤", "error");
    }
    
    applyFilters();
  } catch (error) {
    console.error("Fetch error:", error);
    showToast("無法連接資料庫，請檢查網路連線", "error");
    showEmptyState(true);
  } finally {
    showLoading(false);
  }
}

// Filter and Search Logic
function applyFilters() {
  state.filteredGrades = state.grades.filter(record => {
    // Search filter
    const matchesSearch = 
      record.name.toLowerCase().includes(state.filters.search) ||
      record.student_id.toLowerCase().includes(state.filters.search);
      
    // Subject filter
    const matchesSubject = !state.filters.subject || record.subject === state.filters.subject;
    
    // Status filter (pass/fail)
    let matchesStatus = true;
    if (state.filters.status === "passed") {
      matchesStatus = Number(record.score) >= 60;
    } else if (state.filters.status === "failed") {
      matchesStatus = Number(record.score) < 60;
    }
    
    return matchesSearch && matchesSubject && matchesStatus;
  });
  
  updateDashboard();
  renderTable();
}

// Update Dashboard Statistics Card
function updateDashboard() {
  const total = state.filteredGrades.length;
  elements.statTotal.textContent = total;
  
  if (total === 0) {
    elements.statAverage.textContent = "0.0";
    elements.statPassRate.textContent = "0%";
    elements.statMinMax.textContent = "0 / 0";
    return;
  }
  
  let totalScore = 0;
  let passedCount = 0;
  let highest = -Infinity;
  let lowest = Infinity;
  
  state.filteredGrades.forEach(record => {
    const score = Number(record.score);
    totalScore += score;
    if (score >= 60) passedCount++;
    if (score > highest) highest = score;
    if (score < lowest) lowest = score;
  });
  
  const average = (totalScore / total).toFixed(1);
  const passRate = Math.round((passedCount / total) * 100);
  
  elements.statAverage.textContent = average;
  elements.statPassRate.textContent = `${passRate}%`;
  elements.statMinMax.textContent = `${highest} / ${lowest}`;
}

// Render Table Rows
function renderTable() {
  elements.gradesTbody.innerHTML = "";
  
  if (state.filteredGrades.length === 0) {
    showEmptyState(true);
    elements.gradesTable.classList.add("hidden");
    return;
  }
  
  showEmptyState(false);
  elements.gradesTable.classList.remove("hidden");
  
  state.filteredGrades.forEach(record => {
    const tr = document.createElement("tr");
    
    const isPassed = Number(record.score) >= 60;
    const badgeClass = isPassed ? "badge-success" : "badge-danger";
    const statusText = isPassed ? "及格" : "不及格";
    
    tr.innerHTML = `
      <td>${escapeHTML(record.student_id)}</td>
      <td><strong>${escapeHTML(record.name)}</strong></td>
      <td>${escapeHTML(record.subject)}</td>
      <td><span class="score-value ${isPassed ? '' : 'text-danger'}">${Number(record.score)}</span></td>
      <td><span class="badge ${badgeClass}">${statusText}</span></td>
      <td>${escapeHTML(record.exam_date)}</td>
      <td title="${escapeHTML(record.remarks)}">${escapeHTML(truncateString(record.remarks, 20))}</td>
      <td class="text-right">
        <div class="actions-cell">
          <button class="btn btn-icon btn-text-primary btn-edit" data-id="${record.id}" title="編輯">
            <i class="fa-solid fa-pen-to-square"></i>
          </button>
          <button class="btn btn-icon btn-text-danger btn-delete" data-id="${record.id}" title="刪除">
            <i class="fa-solid fa-trash-can"></i>
          </button>
        </div>
      </td>
    `;
    
    // Add Event Listeners for actions
    tr.querySelector(".btn-edit").addEventListener("click", () => editRecord(record));
    tr.querySelector(".btn-delete").addEventListener("click", () => deleteRecord(record.id));
    
    elements.gradesTbody.appendChild(tr);
  });
}

// Form Operations (Create & Update)
async function handleFormSubmit(e) {
  e.preventDefault();
  
  const id = elements.formId.value;
  const isEdit = !!id;
  
  const payload = {
    action: isEdit ? "update" : "create",
    id: id || undefined,
    student_id: elements.formStudentId.value.trim(),
    name: elements.formName.value.trim(),
    subject: elements.formSubject.value,
    score: Number(elements.formScore.value),
    exam_date: elements.formDate.value,
    remarks: elements.formRemarks.value.trim()
  };
  
  setSubmittingState(true);
  
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      body: JSON.stringify(payload)
    });
    
    const result = await response.json();
    
    if (result.status === "success") {
      showToast(isEdit ? "成績修改成功！" : "新增成績成功！", "success");
      closeModal();
      await fetchGrades(); // Reload data
    } else {
      throw new Error(result.message || "作業處理失敗");
    }
  } catch (error) {
    console.error("Submit error:", error);
    showToast(`存檔失敗：${error.message}`, "error");
  } finally {
    setSubmittingState(false);
  }
}

// Edit Record Trigger
function editRecord(record) {
  openModal(record);
}

// Delete Record Operations
async function deleteRecord(id) {
  if (!confirm("確定要刪除這筆成績紀錄嗎？此動作將無法復原。")) return;
  
  showLoading(true);
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      body: JSON.stringify({ action: "delete", id: id })
    });
    
    const result = await response.json();
    if (result.status === "success") {
      showToast("紀錄已成功刪除！", "success");
      await fetchGrades();
    } else {
      throw new Error(result.message || "刪除作業失敗");
    }
  } catch (error) {
    console.error("Delete error:", error);
    showToast(`刪除失敗：${error.message}`, "error");
    showLoading(false);
  }
}

// Modal State Actions
function openModal(record = null) {
  elements.recordForm.reset();
  
  if (record) {
    elements.modalTitle.textContent = "編輯成績紀錄";
    elements.formId.value = record.id;
    elements.formStudentId.value = record.student_id;
    elements.formName.value = record.name;
    elements.formSubject.value = record.subject;
    elements.formScore.value = record.score;
    elements.formDate.value = record.exam_date;
    elements.formRemarks.value = record.remarks;
    elements.submitFormBtn.textContent = "更新儲存";
  } else {
    elements.modalTitle.textContent = "新增成績紀錄";
    elements.formId.value = "";
    elements.submitFormBtn.textContent = "確認儲存";
    // Set default date to today
    elements.formDate.value = new Date().toISOString().split('T')[0];
  }
  
  elements.recordModal.classList.remove("hidden");
}

function closeModal() {
  elements.recordModal.classList.add("hidden");
  elements.recordForm.reset();
}

// Loading & Submitting State Helpers
function showLoading(show) {
  if (show) {
    elements.loadingState.classList.remove("hidden");
    elements.emptyState.classList.add("hidden");
  } else {
    elements.loadingState.classList.add("hidden");
  }
}

function showEmptyState(show) {
  if (show) {
    elements.emptyState.classList.remove("hidden");
  } else {
    elements.emptyState.classList.add("hidden");
  }
}

function setSubmittingState(submitting) {
  elements.submitFormBtn.disabled = submitting;
  if (submitting) {
    elements.submitFormBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> 正在傳送...';
  } else {
    elements.submitFormBtn.textContent = "確認儲存";
  }
}

// Toast System
let toastTimeout;
function showToast(message, type = "info") {
  clearTimeout(toastTimeout);
  elements.toastMessage.textContent = message;
  
  // Set type style classes
  elements.toast.className = "toast";
  const icon = elements.toast.querySelector(".toast-icon");
  
  if (type === "success") {
    elements.toast.classList.add("toast-success");
    icon.className = "toast-icon fa-solid fa-circle-check";
  } else if (type === "error") {
    elements.toast.classList.add("toast-error");
    icon.className = "toast-icon fa-solid fa-circle-exclamation";
  } else {
    icon.className = "toast-icon fa-solid fa-circle-info";
  }
  
  elements.toast.classList.remove("hidden");
  
  toastTimeout = setTimeout(() => {
    elements.toast.classList.add("hidden");
  }, 3500);
}

// Helpers
function escapeHTML(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

function truncateString(str, num) {
  if (!str) return "";
  if (str.length <= num) return str;
  return str.slice(0, num) + "...";
}
