/**
 * Class Management System - Frontend Engine
 */

class AppEngine {
  constructor() {
    this.currentUser = null;
    this.currentSection = 'dashboard';
    this.init();
  }

  async init() {
    await this.checkAuthStatus();
  }

  showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = 'toast';
    if (type === 'error') toast.style.borderLeft = '4px solid var(--danger)';
    if (type === 'success') toast.style.borderLeft = '4px solid var(--success)';
    toast.innerHTML = `<i class="fa-solid fa-circle-info"></i> ${message}`;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 4000);
  }

  async checkAuthStatus() {
    try {
      const res = await fetch('/api/auth/me');
      if (res.ok) {
        this.currentUser = await res.json();
        this.renderAuthenticatedUI();
      } else {
        this.renderLoginUI();
      }
    } catch (err) {
      this.renderLoginUI();
    }
  }

  async quickLogin(username, password) {
    document.getElementById('login-username').value = username;
    document.getElementById('login-password').value = password;
    const form = document.querySelector('#login-container form');
    form.dispatchEvent(new Event('submit', { cancelable: true, bubbles: true }));
  }

  async handleLogin(event) {
    event.preventDefault();
    const u = document.getElementById('login-username').value;
    const p = document.getElementById('login-password').value;

    try {
      const res = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ username: u, password: p })
      });

      const data = await res.json();
      if (!res.ok) {
        this.showToast(data.detail || 'Đăng nhập thất bại', 'error');
        return;
      }

      this.showToast(`Xin chào, ${data.full_name}!`, 'success');
      await this.checkAuthStatus();
    } catch (err) {
      this.showToast('Lỗi kết nối máy chủ', 'error');
    }
  }

  async logout() {
    await fetch('/api/auth/logout', { method: 'POST' });
    this.currentUser = null;
    this.showToast('Đã đăng xuất', 'info');
    this.renderLoginUI();
  }

  renderLoginUI() {
    document.getElementById('sidebar').style.display = 'none';
    document.getElementById('login-container').style.display = 'block';
    document.getElementById('dashboard-container').style.display = 'none';
  }

  renderAuthenticatedUI() {
    document.getElementById('sidebar').style.display = 'flex';
    document.getElementById('login-container').style.display = 'none';
    document.getElementById('dashboard-container').style.display = 'block';

    const user = this.currentUser;

    document.getElementById('user-display-name').innerText = user.full_name;
    document.getElementById('user-avatar-text').innerText = user.full_name ? user.full_name.charAt(0).toUpperCase() : 'U';

    const badge = document.getElementById('user-role-badge');
    badge.innerText = user.role.toUpperCase();
    badge.className = `badge-role badge-${user.role}`;

    this.buildRoleNavigation(user.role);

    if (user.role === 'admin') this.switchSection('dashboard');
    else if (user.role === 'teacher') this.switchSection('students-list');
    else if (user.role === 'student') this.switchSection('schedule');
  }

  buildRoleNavigation(role) {
    const menu = document.getElementById('nav-menu');
    menu.innerHTML = '';

    let items = [];

    if (role === 'admin') {
      items = [
        { id: 'dashboard', icon: 'fa-chart-pie', label: 'Tổng Quan Hệ Thống' },
        { id: 'admin-users', icon: 'fa-user-shield', label: 'Tạo & Phân Quyền TK' },
        { id: 'admin-courses', icon: 'fa-book', label: 'Môn Học & Lịch Dạy' },
        { id: 'students-list', icon: 'fa-users', label: 'Hồ Sơ Học Sinh' },
        { id: 'schedule', icon: 'fa-calendar-days', label: 'Lịch Dạy & Học' },
        { id: 'attendance', icon: 'fa-clipboard-user', label: 'Điểm Danh Học Sinh' },
        { id: 'grading', icon: 'fa-file-pen', label: 'Nhập Điểm Sinh Viên' },
        { id: 'profile', icon: 'fa-user-gear', label: 'Hồ Sơ Cá Nhân' }
      ];
    } else if (role === 'teacher') {
      items = [
        { id: 'students-list', icon: 'fa-users', label: 'Hồ Sơ Học Sinh' },
        { id: 'schedule', icon: 'fa-calendar-days', label: 'Lịch Dạy Giảng Viên' },
        { id: 'attendance', icon: 'fa-clipboard-user', label: 'Điểm Danh Học Sinh' },
        { id: 'grading', icon: 'fa-file-pen', label: 'Cho Điểm Sinh Viên' },
        { id: 'profile', icon: 'fa-user-gear', label: 'Hồ Sơ Cá Nhân' }
      ];
    } else if (role === 'student') {
      items = [
        { id: 'schedule', icon: 'fa-calendar-days', label: 'Lịch Học Cá Nhân' },
        { id: 'registration', icon: 'fa-folder-plus', label: 'Đăng Ký Môn Học' },
        { id: 'my-grades', icon: 'fa-award', label: 'Bảng Điểm Cá Nhân' },
        { id: 'tuition', icon: 'fa-wallet', label: 'Tra Cứu Học Phí' },
        { id: 'profile', icon: 'fa-user-gear', label: 'Hồ Sơ Cá Nhân' }
      ];
    }

    items.forEach(item => {
      const li = document.createElement('li');
      li.className = `nav-item ${item.id === this.currentSection ? 'active' : ''}`;
      li.dataset.section = item.id;
      li.innerHTML = `<i class="fa-solid ${item.icon} nav-icon"></i> <span>${item.label}</span>`;
      li.onclick = () => this.switchSection(item.id);
      menu.appendChild(li);
    });
  }

  switchSection(sectionId) {
    this.currentSection = sectionId;

    document.querySelectorAll('.nav-item').forEach(el => {
      if (el.dataset.section === sectionId || el.getAttribute('onclick')?.includes(sectionId)) {
        el.classList.add('active');
      } else {
        el.classList.remove('active');
      }
    });

    document.querySelectorAll('.content-sec').forEach(sec => sec.style.display = 'none');

    const targetSec = document.getElementById(`sec-${sectionId}`);
    if (targetSec) {
      targetSec.style.display = 'block';
    }

    const titles = {
      'dashboard': { title: 'Tổng Quan Hệ Thống', sub: 'Thống kê tổng quan và thông tin quản trị' },
      'admin-users': { title: 'Tạo & Phân Quyền Tài Khoản', sub: 'Quản lý tài khoản Admin, Giáo viên và Sinh viên' },
      'admin-courses': { title: 'Quản Lý Môn Học & Xếp Lịch Dạy', sub: 'Tạo môn học mới và phân công lịch dạy cho giáo viên' },
      'students-list': { title: 'Hồ Sơ Học Sinh / Sinh Viên', sub: 'Danh sách và thông tin chi tiết học sinh trong hệ thống' },
      'schedule': { title: 'Lịch Dạy & Học', sub: 'Tra cứu thời khóa biểu giảng dạy và học tập' },
      'attendance': { title: 'Điểm Danh Học Sinh', sub: 'Quản lý trạng thái chuyên cần theo từng buổi học' },
      'grading': { title: 'Cho Điểm Sinh Viên', sub: 'Nhập điểm giữa kỳ, cuối kỳ và đánh giá kết quả học tập' },
      'registration': { title: 'Đăng Ký Môn Học', sub: 'Đăng ký các môn học mở trong học kỳ' },
      'my-grades': { title: 'Bảng Điểm Cá Nhân', sub: 'Xem điểm chi tiết và kết quả học tập các môn' },
      'tuition': { title: 'Tra Cứu Học Phí', sub: 'Chi tiết học phí từng môn và tổng tiền phải nộp' },
      'profile': { title: 'Hồ Sơ Cá Nhân & Mật Khẩu', sub: 'Cập nhật thông tin tài khoản và đổi mật khẩu' }
    };

    if (titles[sectionId]) {
      const h = document.getElementById('page-heading');
      const s = document.getElementById('page-subheading');
      if (h) h.innerText = titles[sectionId].title;
      if (s) s.innerText = titles[sectionId].sub;
    }

    try {
      if (sectionId === 'dashboard') this.loadAdminDashboardStats();
      if (sectionId === 'profile') this.loadProfile();
      if (sectionId === 'students-list') this.loadStudentList();
      if (sectionId === 'schedule') this.loadScheduleView();
      if (sectionId === 'attendance') this.loadAttendanceSchedules();
      if (sectionId === 'grading') this.loadGradingCourses();
      if (sectionId === 'registration') this.loadStudentCoursesRegistration();
      if (sectionId === 'my-grades') this.loadStudentGrades();
      if (sectionId === 'tuition') this.loadStudentTuition();
      if (sectionId === 'admin-users') this.loadAdminUsers();
      if (sectionId === 'admin-courses') this.loadAdminCourses();
    } catch (err) {
      console.error('Error switching section:', err);
    }
  }

  async loadAdminDashboardStats() {
    if (this.currentUser.role !== 'admin') return;
    document.getElementById('admin-stats-grid').style.display = 'grid';

    const res = await fetch('/api/admin/stats');
    if (res.ok) {
      const stats = await res.json();
      document.getElementById('stat-teachers').innerText = stats.teachers_count;
      document.getElementById('stat-students').innerText = stats.students_count;
      document.getElementById('stat-courses').innerText = stats.courses_count;
      document.getElementById('stat-schedules').innerText = stats.schedules_count;
    }
  }

  async loadProfile() {
    const u = this.currentUser;
    document.getElementById('profile-name-text').innerText = u.full_name;
    document.getElementById('profile-role-text').innerText = u.role.toUpperCase();
    document.getElementById('profile-big-avatar').innerText = u.full_name ? u.full_name.charAt(0).toUpperCase() : 'U';

    document.getElementById('prof-fullname').value = u.full_name || '';
    document.getElementById('prof-title').value = u.title || '';
    document.getElementById('prof-age').value = u.age || '';
    document.getElementById('prof-department').value = u.department || '';
    document.getElementById('prof-email').value = u.email || '';
    document.getElementById('prof-phone').value = u.phone || '';
  }

  async saveProfile(e) {
    e.preventDefault();
    const payload = {
      full_name: document.getElementById('prof-fullname').value,
      title: document.getElementById('prof-title').value,
      age: parseInt(document.getElementById('prof-age').value) || null,
      department: document.getElementById('prof-department').value,
      email: document.getElementById('prof-email').value,
      phone: document.getElementById('prof-phone').value
    };

    const res = await fetch('/api/auth/profile', {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      this.currentUser = await res.json();
      this.showToast('Đã cập nhật hồ sơ cá nhân thành công!', 'success');
      this.loadProfile();
      document.getElementById('user-display-name').innerText = this.currentUser.full_name;
    } else {
      this.showToast('Lỗi khi cập nhật hồ sơ', 'error');
    }
  }

  async changePassword(e) {
    e.preventDefault();
    const oldPassword = document.getElementById('change-old-password').value;
    const newPassword = document.getElementById('change-new-password').value;
    const confirmPassword = document.getElementById('change-confirm-password').value;

    if (newPassword !== confirmPassword) {
      this.showToast('Mật khẩu mới và xác nhận mật khẩu không khớp!', 'error');
      return;
    }

    if (newPassword.length < 6) {
      this.showToast('Mật khẩu mới phải có ít nhất 6 ký tự!', 'error');
      return;
    }

    try {
      const res = await fetch('/api/auth/change-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          old_password: oldPassword,
          new_password: newPassword
        })
      });

      const data = await res.json();
      if (res.ok) {
        this.showToast(data.message || 'Đổi mật khẩu thành công!', 'success');
        document.getElementById('change-old-password').value = '';
        document.getElementById('change-new-password').value = '';
        document.getElementById('change-confirm-password').value = '';
      } else {
        this.showToast(data.detail || 'Lỗi khi đổi mật khẩu', 'error');
      }
    } catch (err) {
      this.showToast('Lỗi hệ thống khi đổi mật khẩu', 'error');
    }
  }

  async loadStudentList() {
    const search = document.getElementById('search-student-input')?.value || '';
    const res = await fetch(`/api/teacher/students?search=${encodeURIComponent(search)}`);
    const tbody = document.getElementById('student-table-body');
    tbody.innerHTML = '';

    if (res.ok) {
      const students = await res.json();
      if (students.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">Không tìm thấy hồ sơ sinh viên nào.</td></tr>`;
        return;
      }
      students.forEach(s => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><b>${s.code || 'SV-' + s.id}</b></td>
          <td>${s.full_name}</td>
          <td>${s.title || 'Sinh viên'}</td>
          <td>${s.department || '-'}</td>
          <td>${s.email || '-'}</td>
          <td>${s.phone || '-'}</td>
          <td>${s.age || '-'}</td>
        `;
        tbody.appendChild(tr);
      });
    }
  }

  async loadScheduleView() {
    const week = document.getElementById('filter-week-select').value;
    const month = document.getElementById('filter-month-select').value;
    let url = '/api/teacher/schedules';
    if (this.currentUser.role === 'student') url = '/api/student/schedules';

    const params = new URLSearchParams();
    if (week) params.append('week_number', week);
    if (month) params.append('month_number', month);

    const res = await fetch(`${url}?${params.toString()}`);
    const container = document.getElementById('schedule-cards-container');
    container.innerHTML = '';

    if (res.ok) {
      const schedules = await res.json();
      if (schedules.length === 0) {
        container.innerHTML = `<div style="grid-column: 1/-1; color: var(--text-muted); text-align: center; padding: 40px;" class="glass-panel">Không có lịch học/dạy nào trong thời gian được chọn.</div>`;
        return;
      }
      schedules.forEach(s => {
        const card = document.createElement('div');
        card.className = 'glass-panel schedule-card';
        card.innerHTML = `
          <div class="day-badge"><i class="fa-solid fa-calendar-day"></i> ${s.day_of_week} (Tuần ${s.week_number})</div>
          <div class="time"><i class="fa-solid fa-clock"></i> ${s.start_time} - ${s.end_time}</div>
          <h3 style="font-size: 16px;">${s.course_name} (${s.course_code})</h3>
          <p style="font-size: 13px; color: var(--text-muted);"><i class="fa-solid fa-location-dot"></i> ${s.room}</p>
          <p style="font-size: 12px; color: var(--primary);"><i class="fa-solid fa-chalkboard-user"></i> Giảng viên: ${s.teacher_name}</p>
        `;
        container.appendChild(card);
      });
    }
  }

  async loadAttendanceSchedules() {
    const select = document.getElementById('att-schedule-select');
    select.innerHTML = '<option value="">-- Chọn lịch dạy --</option>';

    const res = await fetch('/api/teacher/schedules');
    if (res.ok) {
      const schedules = await res.json();
      schedules.forEach(s => {
        const opt = document.createElement('option');
        opt.value = s.id;
        opt.innerText = `${s.course_name} | ${s.day_of_week} (${s.start_time}-${s.end_time}) | Phòng: ${s.room}`;
        select.appendChild(opt);
      });
    }
  }

  async loadStudentsForAttendance() {
    const scheduleId = document.getElementById('att-schedule-select').value;
    const dateVal = document.getElementById('att-date-input').value;
    const tbody = document.getElementById('attendance-table-body');
    tbody.innerHTML = '';

    if (!scheduleId) return;

    const resStudents = await fetch(`/api/teacher/schedules/${scheduleId}/students`);
    const resAtt = await fetch(`/api/teacher/attendance/${scheduleId}?attendance_date=${dateVal}`);

    if (resStudents.ok) {
      const students = await resStudents.json();
      let attMap = {};
      if (resAtt.ok) {
        const attRecords = await resAtt.json();
        attRecords.forEach(r => attMap[r.student_id] = r);
      }

      students.forEach(st => {
        const currentAtt = attMap[st.id] || { status: 'Có mặt', note: '' };
        const tr = document.createElement('tr');
        tr.dataset.studentId = st.id;
        tr.innerHTML = `
          <td><b>${st.code || 'SV-' + st.id}</b></td>
          <td>${st.full_name}</td>
          <td>
            <select class="form-control att-status-select" style="width: 140px;">
              <option value="Có mặt" ${currentAtt.status === 'Có mặt' ? 'selected' : ''}>✅ Có mặt</option>
              <option value="Vắng mặt" ${currentAtt.status === 'Vắng mặt' ? 'selected' : ''}>❌ Vắng mặt</option>
              <option value="Đi muộn" ${currentAtt.status === 'Đi muộn' ? 'selected' : ''}>⚠️ Đi muộn</option>
              <option value="Có phép" ${currentAtt.status === 'Có phép' ? 'selected' : ''}>📝 Có phép</option>
            </select>
          </td>
          <td>
            <input type="text" class="form-control att-note-input" placeholder="Ghi chú thêm..." value="${currentAtt.note || ''}">
          </td>
        `;
        tbody.appendChild(tr);
      });
    }
  }

  async submitAttendance() {
    const scheduleId = parseInt(document.getElementById('att-schedule-select').value);
    const dateVal = document.getElementById('att-date-input').value;

    if (!scheduleId || !dateVal) {
      this.showToast('Vui lòng chọn lịch dạy và ngày điểm danh', 'error');
      return;
    }

    const rows = document.querySelectorAll('#attendance-table-body tr');
    const records = [];

    rows.forEach(tr => {
      const studentId = parseInt(tr.dataset.studentId);
      const status = tr.querySelector('.att-status-select').value;
      const note = tr.querySelector('.att-note-input').value;
      if (studentId) {
        records.push({ student_id: studentId, status, note });
      }
    });

    const res = await fetch('/api/teacher/attendance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ schedule_id: scheduleId, attendance_date: dateVal, records })
    });

    if (res.ok) {
      this.showToast('Lưu kết quả điểm danh thành công!', 'success');
    } else {
      this.showToast('Lỗi khi lưu điểm danh', 'error');
    }
  }

  async loadGradingCourses() {
    const select = document.getElementById('grading-course-select');
    select.innerHTML = '<option value="">-- Chọn môn học --</option>';

    const res = await fetch('/api/teacher/courses');
    if (res.ok) {
      const courses = await res.json();
      courses.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id;
        opt.innerText = `${c.course_name} (${c.course_code})`;
        select.appendChild(opt);
      });
    }
  }

  async loadGradesForCourse() {
    const courseId = document.getElementById('grading-course-select').value;
    const tbody = document.getElementById('grading-table-body');
    tbody.innerHTML = '';

    if (!courseId) return;

    const res = await fetch(`/api/teacher/courses/${courseId}/grades`);
    if (res.ok) {
      const grades = await res.json();
      if (grades.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">Chưa có sinh viên nào đăng ký môn này.</td></tr>`;
        return;
      }

      grades.forEach(g => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><b>${g.student_code || 'SV-' + g.student_id}</b></td>
          <td>${g.student_name}</td>
          <td><input type="number" step="0.1" min="0" max="10" class="form-control input-mid" value="${g.midterm_score ?? ''}" style="width:90px;"></td>
          <td><input type="number" step="0.1" min="0" max="10" class="form-control input-fin" value="${g.final_score ?? ''}" style="width:90px;"></td>
          <td><b style="color:var(--primary); font-size:16px;">${g.total_score ?? '-'}</b></td>
          <td><input type="text" class="form-control input-note" value="${g.note || ''}" placeholder="Ghi chú..."></td>
          <td>
            <button onclick="app.saveStudentGrade(${g.student_id}, ${courseId}, this)" class="btn btn-primary btn-sm">
              <i class="fa-solid fa-floppy-disk"></i> Lưu Điểm
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }
  }

  async saveStudentGrade(studentId, courseId, btn) {
    const tr = btn.closest('tr');
    const midVal = tr.querySelector('.input-mid').value;
    const finVal = tr.querySelector('.input-fin').value;
    const noteVal = tr.querySelector('.input-note').value;

    const payload = {
      student_id: studentId,
      course_id: courseId,
      midterm_score: midVal !== '' ? parseFloat(midVal) : null,
      final_score: finVal !== '' ? parseFloat(finVal) : null,
      note: noteVal
    };

    const res = await fetch('/api/teacher/grades', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      this.showToast('Đã nhập điểm thành công!', 'success');
      this.loadGradesForCourse();
    } else {
      this.showToast('Lỗi khi lưu điểm', 'error');
    }
  }

  async loadStudentCoursesRegistration() {
    const res = await fetch('/api/student/courses');
    const tbody = document.getElementById('registration-table-body');
    tbody.innerHTML = '';

    if (res.ok) {
      const courses = await res.json();
      courses.forEach(c => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><b>${c.course_code}</b></td>
          <td>${c.course_name}</td>
          <td>${c.credits} tín chỉ</td>
          <td>${c.department || '-'}</td>
          <td><span style="font-size:12px; color:var(--text-muted);">${c.description || ''}</span></td>
          <td>
            ${c.is_enrolled ? 
              `<button onclick="app.unregisterCourse(${c.id})" class="btn btn-danger btn-sm"><i class="fa-solid fa-trash"></i> Hủy Đăng Ký</button>` : 
              `<button onclick="app.registerCourse(${c.id})" class="btn btn-success btn-sm"><i class="fa-solid fa-plus"></i> Đăng Ký Môn</button>`
            }
          </td>
        `;
        tbody.appendChild(tr);
      });
    }
  }

  async registerCourse(courseId) {
    const res = await fetch(`/api/student/register/${courseId}`, { method: 'POST' });
    if (res.ok) {
      this.showToast('Đăng ký môn học thành công!', 'success');
      this.loadStudentCoursesRegistration();
    } else {
      const err = await res.json();
      this.showToast(err.detail || 'Lỗi đăng ký môn học', 'error');
    }
  }

  async unregisterCourse(courseId) {
    const res = await fetch(`/api/student/unregister/${courseId}`, { method: 'DELETE' });
    if (res.ok) {
      this.showToast('Hủy đăng ký môn học thành công', 'info');
      this.loadStudentCoursesRegistration();
    }
  }

  async loadStudentGrades() {
    const res = await fetch('/api/student/grades');
    const tbody = document.getElementById('my-grades-table-body');
    tbody.innerHTML = '';

    if (res.ok) {
      const grades = await res.json();
      if (grades.length === 0) {
        tbody.innerHTML = `<tr><td colspan="7" style="text-align:center; color:var(--text-muted);">Bạn chưa đăng ký môn học nào.</td></tr>`;
        return;
      }
      grades.forEach(g => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><b>${g.course_code}</b></td>
          <td>${g.course_name}</td>
          <td>${g.credits} tín chỉ</td>
          <td>${g.midterm_score ?? '-'}</td>
          <td>${g.final_score ?? '-'}</td>
          <td><b style="color:var(--primary); font-size:16px;">${g.total_score ?? '-'}</b></td>
          <td>${g.note || '-'}</td>
        `;
        tbody.appendChild(tr);
      });
    }
  }

  async loadStudentTuition() {
    const res = await fetch('/api/student/tuition');
    const tbody = document.getElementById('tuition-table-body');
    tbody.innerHTML = '';

    if (res.ok) {
      const data = await res.json();
      document.getElementById('tuition-total-credits').innerText = `${data.total_credits} tín chỉ`;
      document.getElementById('tuition-total-fee').innerText = `${data.total_tuition_fee.toLocaleString('vi-VN')} VNĐ`;
      document.getElementById('tuition-payment-status').innerText = data.payment_status;

      if (data.courses.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center; color:var(--text-muted);">Bạn chưa đăng ký môn học nào trong kỳ này.</td></tr>`;
        return;
      }

      data.courses.forEach(c => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><b>${c.course_code}</b></td>
          <td>${c.course_name}</td>
          <td>${c.credits} tín chỉ</td>
          <td>${c.fee_per_credit.toLocaleString('vi-VN')} VNĐ</td>
          <td><b style="color:var(--success); font-size:15px;">${c.total_course_fee.toLocaleString('vi-VN')} VNĐ</b></td>
          <td>${c.term}</td>
        `;
        tbody.appendChild(tr);
      });
    }
  }

  async loadAdminUsers() {
    const res = await fetch('/api/admin/users');
    const tbody = document.getElementById('admin-users-table-body');
    tbody.innerHTML = '';

    if (res.ok) {
      const users = await res.json();
      users.forEach(u => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td>#${u.id}</td>
          <td><b>${u.username}</b></td>
          <td>${u.full_name}</td>
          <td>
            <select class="form-control" onchange="app.changeUserRole(${u.id}, this.value)" style="width:130px; padding:4px 8px; font-size:12px;">
              <option value="student" ${u.role === 'student' ? 'selected' : ''}>Sinh Viên</option>
              <option value="teacher" ${u.role === 'teacher' ? 'selected' : ''}>Giáo Viên</option>
              <option value="admin" ${u.role === 'admin' ? 'selected' : ''}>Admin</option>
            </select>
          </td>
          <td>${u.code || '-'}</td>
          <td>${u.department || '-'}</td>
          <td>
            <button onclick="app.deleteUserAccount(${u.id})" class="btn btn-danger btn-sm">
              <i class="fa-solid fa-user-xmark"></i> Xóa
            </button>
          </td>
        `;
        tbody.appendChild(tr);
      });
    }
  }

  async changeUserRole(userId, newRole) {
    const res = await fetch(`/api/admin/users/${userId}/role?new_role=${newRole}`, { method: 'PUT' });
    if (res.ok) {
      this.showToast('Phân quyền tài khoản thành công!', 'success');
      this.loadAdminUsers();
    } else {
      const err = await res.json();
      this.showToast(err.detail || 'Lỗi phân quyền', 'error');
    }
  }

  async deleteUserAccount(userId) {
    if (!confirm('Bạn có chắc chắn muốn xóa tài khoản này?')) return;
    const res = await fetch(`/api/admin/users/${userId}`, { method: 'DELETE' });
    if (res.ok) {
      this.showToast('Đã xóa tài khoản thành công', 'info');
      this.loadAdminUsers();
    } else {
      const err = await res.json();
      this.showToast(err.detail || 'Lỗi khi xóa tài khoản', 'error');
    }
  }

  showCreateUserModal() {
    document.getElementById('modal-create-user').classList.add('active');
  }

  async handleCreateUser(e) {
    e.preventDefault();
    const payload = {
      username: document.getElementById('new-u-username').value,
      password: document.getElementById('new-u-password').value,
      role: document.getElementById('new-u-role').value,
      full_name: document.getElementById('new-u-fullname').value,
      code: document.getElementById('new-u-code').value
    };

    const res = await fetch('/api/admin/users', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      this.showToast('Tạo tài khoản và phân quyền thành công!', 'success');
      this.closeModal('modal-create-user');
      this.loadAdminUsers();
    } else {
      const err = await res.json();
      this.showToast(err.detail || 'Lỗi tạo tài khoản', 'error');
    }
  }

  async loadAdminCourses() {
    const res = await fetch('/api/admin/courses');
    const tbody = document.getElementById('admin-courses-table-body');
    tbody.innerHTML = '';

    if (res.ok) {
      const courses = await res.json();
      courses.forEach(c => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
          <td><b>${c.course_code}</b></td>
          <td>${c.course_name}</td>
          <td>${c.credits} tín chỉ</td>
          <td>${c.department || '-'}</td>
          <td>${c.term}</td>
        `;
        tbody.appendChild(tr);
      });
    }
  }

  showCreateCourseModal() {
    document.getElementById('modal-create-course').classList.add('active');
  }

  async handleCreateCourse(e) {
    e.preventDefault();
    const payload = {
      course_code: document.getElementById('c-code').value,
      course_name: document.getElementById('c-name').value,
      credits: parseInt(document.getElementById('c-credits').value),
      department: document.getElementById('c-dept').value
    };

    const res = await fetch('/api/admin/courses', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      this.showToast('Tạo môn học mới thành công!', 'success');
      this.closeModal('modal-create-course');
      this.loadAdminCourses();
    }
  }

  async showCreateScheduleModal() {
    document.getElementById('modal-create-schedule').classList.add('active');
    
    const resC = await fetch('/api/admin/courses');
    const selC = document.getElementById('sch-course-select');
    selC.innerHTML = '';
    if (resC.ok) {
      const courses = await resC.json();
      courses.forEach(c => {
        selC.innerHTML += `<option value="${c.id}">${c.course_name} (${c.course_code})</option>`;
      });
    }

    const resT = await fetch('/api/admin/users?role=teacher');
    const selT = document.getElementById('sch-teacher-select');
    selT.innerHTML = '';
    if (resT.ok) {
      const teachers = await resT.json();
      teachers.forEach(t => {
        selT.innerHTML += `<option value="${t.id}">${t.full_name} (${t.code || t.username})</option>`;
      });
    }
  }

  async handleCreateSchedule(e) {
    e.preventDefault();
    const payload = {
      course_id: parseInt(document.getElementById('sch-course-select').value),
      teacher_id: parseInt(document.getElementById('sch-teacher-select').value),
      room: document.getElementById('sch-room').value,
      day_of_week: document.getElementById('sch-day').value,
      week_number: parseInt(document.getElementById('sch-week').value),
      start_time: document.getElementById('sch-start').value,
      end_time: document.getElementById('sch-end').value,
      month_number: 9
    };

    const res = await fetch('/api/admin/schedules', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      this.showToast('Xếp lịch dạy cho giáo viên thành công!', 'success');
      this.closeModal('modal-create-schedule');
    }
  }

  closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
  }
}

const app = new AppEngine();
