/**
 * MidtermVibe — Desktop Learning SPA Logic
 * Real Exam Mode: Answer all questions -> Navigate freely -> Submit at end -> Review score & explanations
 */

let state = {
  questions: [],
  currentQuizList: [],
  currentIndex: 0,
  isExamMode: true,        // True for Random Quiz (Exam), False for single Day practice
  isSubmitted: false,       // Submitted state
  examUserAnswers: {},      // { [qId]: chosenIdx }
  notes: localStorage.getItem('midtermvibe_notes') || '',
  activeView: 'home'
};

function refreshIcons() {
  if (window.lucide) {
    lucide.createIcons();
  }
}

async function initApp() {
  try {
    let qRes;
    try {
      qRes = await fetch('/api/questions');
      if (!qRes.ok) throw new Error('API offline');
    } catch(e) {
      qRes = await fetch('/static/data/questions.json');
    }
    const qData = await qRes.json();
    state.questions = qData.questions || [];

    renderTopicsGrid();
    updateStatsDisplay();

    const notesArea = document.getElementById('personalNotesTextarea');
    if (notesArea) {
      notesArea.value = state.notes;
      notesArea.addEventListener('input', (e) => {
        state.notes = e.target.value;
        localStorage.setItem('midtermvibe_notes', state.notes);
      });
    }

    setupEventListeners();
    refreshIcons();
  } catch (err) {
    console.error('Error initializing app:', err);
  }
}

// Start a Random Exam (30 questions)
async function startRandomQuiz(customTrack, customDiff) {
  const track = customTrack || document.getElementById('filterTrackSelect').value;
  const diff = customDiff || document.getElementById('filterDiffSelect').value;

  let url = `/api/questions?track=${encodeURIComponent(track)}&difficulty=${encodeURIComponent(diff)}`;

  try {
    const res = await fetch(url);
    const data = await res.json();
    let qList = data.questions || [];
    
    // Shuffle and pick 30 questions
    qList.sort(() => Math.random() - 0.5);
    state.currentQuizList = qList.slice(0, 30);
    state.currentIndex = 0;
    state.isExamMode = true;
    state.isSubmitted = false;
    state.examUserAnswers = {};

    document.getElementById('examResultBanner').classList.add('hidden');
    document.getElementById('quizBackBtnText').textContent = 'Trang chủ';
    document.getElementById('examModeBadge').textContent = 'ĐỀ THI TỔNG HỢP';

    switchView('random-quiz');
    renderCurrentQuestion();
    renderPalette();
  } catch (e) {
    console.error('Failed to start exam:', e);
  }
}

// Start a Day-specific practice
async function startDayQuiz(dayName) {
  try {
    const res = await fetch(`/api/questions?day=${encodeURIComponent(dayName)}`);
    const data = await res.json();
    let qList = data.questions || [];
    
    state.currentQuizList = qList;
    state.currentIndex = 0;
    state.isExamMode = true; // Also treat as complete test for this Day
    state.isSubmitted = false;
    state.examUserAnswers = {};

    document.getElementById('examResultBanner').classList.add('hidden');
    document.getElementById('quizBackBtnText').textContent = 'Danh sách Day';
    document.getElementById('examModeBadge').textContent = `ÔN TẬP ${dayName.toUpperCase()}`;

    switchView('random-quiz');
    renderCurrentQuestion();
    renderPalette();
  } catch (e) {
    console.error('Failed to start day quiz:', e);
  }
}

// Render Palette Grid (1 to N)
function renderPalette() {
  const container = document.getElementById('paletteGrid');
  if (!container) return;
  container.innerHTML = '';

  state.currentQuizList.forEach((q, idx) => {
    const item = document.createElement('div');
    item.className = 'palette-item';
    item.textContent = idx + 1;
    
    if (idx === state.currentIndex) {
      item.classList.add('current');
    }

    const chosen = state.examUserAnswers[q.id];
    if (chosen !== undefined) {
      if (!state.isSubmitted) {
        item.classList.add('answered');
      } else {
        if (chosen === q.correct_index) {
          item.classList.add('correct');
        } else {
          item.classList.add('incorrect');
        }
      }
    }

    item.onclick = () => {
      state.currentIndex = idx;
      renderCurrentQuestion();
      renderPalette();
    };

    container.appendChild(item);
  });
}

function renderCurrentQuestion() {
  const q = state.currentQuizList[state.currentIndex];
  if (!q) return;

  const total = state.currentQuizList.length;
  const currNum = state.currentIndex + 1;

  document.getElementById('qTrackBadge').textContent = q.track;
  document.getElementById('qDayBadge').textContent = q.day;
  
  const diffBadge = document.getElementById('qDiffBadge');
  diffBadge.textContent = q.difficulty;
  diffBadge.className = `badge-editorial badge-editorial-diff`;

  document.getElementById('qQuestionText').textContent = q.question.replace(/^\[.*?\]\s*/, '');
  document.getElementById('quizProgressText').textContent = `${currNum}/${total}`;

  // Top Submit Button visibility
  const topSubmitBtn = document.getElementById('topSubmitExamBtn');
  if (topSubmitBtn) {
    topSubmitBtn.classList.toggle('hidden', state.isSubmitted);
  }

  // Render Options
  const container = document.getElementById('optionsContainer');
  container.innerHTML = '';
  
  const chosenIdx = state.examUserAnswers[q.id];

  q.options.forEach((optText, idx) => {
    const row = document.createElement('div');
    row.className = 'sleek-option-row';
    if (chosenIdx === idx) {
      row.classList.add('selected');
    }

    row.innerHTML = `
      <div class="radio-circle">
        <div class="radio-circle-inner"></div>
      </div>
      <div class="option-row-text">${optText}</div>
    `;

    if (!state.isSubmitted) {
      // In Exam Mode: user selects answer freely
      row.onclick = () => selectExamOption(idx);
    } else {
      // In Post-Exam Review Mode: show correct & incorrect highlights
      if (idx === q.correct_index) {
        row.classList.add('correct');
      } else if (chosenIdx === idx) {
        row.classList.add('incorrect');
      }
    }

    container.appendChild(row);
  });

  // Explanation Box handling (ONLY shown in Post-Exam Review)
  const expBox = document.getElementById('explanationBox');
  if (state.isSubmitted) {
    expBox.classList.remove('hidden');
    const isCorrect = chosenIdx === q.correct_index;
    const statusText = isCorrect ? '✅ Bạn đã trả lời đúng!' : '❌ Đáp án của bạn chưa chính xác!';
    document.getElementById('explanationStatus').textContent = statusText;
    document.getElementById('explanationContent').textContent = q.explanation;
    
    const slideRef = document.getElementById('slideRefLink');
    slideRef.textContent = q.slide_ref || 'Slide bài giảng';
  } else {
    expBox.classList.add('hidden');
  }

  // Navigation Buttons
  const prevBtn = document.getElementById('examPrevBtn');
  const nextBtn = document.getElementById('examNextBtn');
  const submitBtn = document.getElementById('examSubmitBtn');

  prevBtn.disabled = (state.currentIndex === 0);
  prevBtn.style.opacity = (state.currentIndex === 0) ? '0.4' : '1';

  if (!state.isSubmitted) {
    if (state.currentIndex === total - 1) {
      nextBtn.classList.add('hidden');
      submitBtn.classList.remove('hidden');
    } else {
      nextBtn.classList.remove('hidden');
      submitBtn.classList.add('hidden');
    }
  } else {
    nextBtn.classList.remove('hidden');
    submitBtn.classList.add('hidden');
    nextBtn.textContent = (state.currentIndex === total - 1) ? 'Quay lại câu 1' : 'Câu tiếp theo →';
  }

  renderPalette();
  refreshIcons();
}

function selectExamOption(idx) {
  if (state.isSubmitted) return;
  const q = state.currentQuizList[state.currentIndex];
  if (!q) return;

  state.examUserAnswers[q.id] = idx;
  renderCurrentQuestion();
}

function goToPrevQuestion() {
  if (state.currentIndex > 0) {
    state.currentIndex--;
    renderCurrentQuestion();
  }
}

function goToNextQuestion() {
  const total = state.currentQuizList.length;
  if (state.currentIndex < total - 1) {
    state.currentIndex++;
    renderCurrentQuestion();
  } else if (state.isSubmitted) {
    state.currentIndex = 0;
    renderCurrentQuestion();
  }
}

function submitExam() {
  const total = state.currentQuizList.length;
  const answeredCount = Object.keys(state.examUserAnswers).length;

  if (answeredCount < total) {
    const confirmSubmit = confirm(`Bạn mới làm ${answeredCount}/${total} câu. Bạn có chắc chắn muốn nộp bài thi ngay bây giờ không?`);
    if (!confirmSubmit) return;
  } else {
    const confirmSubmit = confirm(`Bạn đã hoàn thành ${total}/${total} câu hỏi. Xác nhận nộp bài thi?`);
    if (!confirmSubmit) return;
  }

  state.isSubmitted = true;

  // Calculate score
  let correctCount = 0;
  state.currentQuizList.forEach(q => {
    if (state.examUserAnswers[q.id] === q.correct_index) {
      correctCount++;
    }
  });

  const percent = Math.round((correctCount / total) * 100);

  // Show Result Banner
  const banner = document.getElementById('examResultBanner');
  banner.classList.remove('hidden');
  document.getElementById('examScorePercent').textContent = `${percent}%`;
  document.getElementById('examResultTitle').textContent = percent >= 80 ? '🎉 Xuất Sắc!' : (percent >= 50 ? '👍 Đạt Yêu Cầu!' : '⚠️ Cần Ôn Tập Thêm!');
  document.getElementById('examResultDesc').textContent = `Bạn đã trả lời đúng ${correctCount}/${total} câu hỏi (${percent}%). Hãy xem lại chi tiết từng câu bên dưới.`;

  state.currentIndex = 0;
  renderCurrentQuestion();
  renderPalette();
  updateStatsDisplay();

  // Scroll to top of workspace
  const workspace = document.querySelector('.content-workspace');
  if (workspace) workspace.scrollTop = 0;
}

function renderTopicsGrid() {
  const container = document.getElementById('topicsGrid');
  if (!container) return;

  const tracks = {
    "Phase 1: COMP2010 (AI Application & Agents)": {},
    "Track 2: BIOM3010 (AI Infrastructure & LLMOps)": {}
  };

  state.questions.forEach(q => {
    const tKey = q.track.includes("Phase 1") ? "Phase 1: COMP2010 (AI Application & Agents)" : "Track 2: BIOM3010 (AI Infrastructure & LLMOps)";
    if (!tracks[tKey][q.day]) {
      tracks[tKey][q.day] = {
        topic: q.topic,
        count: 0,
        day: q.day,
        questions: []
      };
    }
    tracks[tKey][q.day].count++;
    tracks[tKey][q.day].questions.push(q);
  });

  let html = '';
  for (const [trackTitle, daysObj] of Object.entries(tracks)) {
    html += `
      <div class="track-block mb-4">
        <h3 class="track-block-title font-editorial">${trackTitle}</h3>
        <div class="topics-cards-container">
    `;

    for (const [dayName, dayInfo] of Object.entries(daysObj)) {
      html += `
        <div class="topic-card card" onclick="startDayQuiz('${dayName}')">
          <div class="topic-card-header">
            <span class="badge-editorial badge-editorial-day">${dayName}</span>
            <span class="text-xs text-muted font-bold">${dayInfo.count} câu hỏi</span>
          </div>
          <h4 class="topic-card-name font-editorial">${dayInfo.topic}</h4>
          <div class="topic-card-progress mt-2">
            <div class="flex-between mt-2">
              <span class="text-xs text-muted">Trọn bộ 45 câu</span>
              <span class="text-xs text-terracotta font-bold topic-card-cta">Làm bài thi Day này ➔</span>
            </div>
          </div>
        </div>
      `;
    }

    html += `</div></div>`;
  }

  container.innerHTML = html;
}

function updateStatsDisplay() {
  document.getElementById('headerCompletedCount').textContent = `Tổng kho: ${state.questions.length} câu`;
}

function switchView(viewId) {
  state.activeView = viewId;
  document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));

  const activeBtn = document.querySelector(`.nav-item[data-view="${viewId}"]`);
  if (activeBtn) activeBtn.classList.add('active');

  const panelMap = {
    'home': 'viewHome',
    'random-quiz': 'viewRandomQuiz',
    'topic-quiz': 'viewTopicQuiz'
  };

  const targetPanel = document.getElementById(panelMap[viewId]);
  if (targetPanel) targetPanel.classList.add('active');

  const titles = {
    'home': 'Trang chủ',
    'random-quiz': 'Đề thi ngẫu nhiên',
    'topic-quiz': 'Ôn tập theo Day'
  };
  document.getElementById('currentViewTitle').textContent = titles[viewId] || '';
  
  if (viewId === 'topic-quiz') {
    renderTopicsGrid();
  } else if (viewId === 'random-quiz') {
    if (!state.currentQuizList || state.currentQuizList.length === 0) {
      startRandomQuiz();
    } else {
      renderCurrentQuestion();
    }
  }
  
  refreshIcons();
}

function setupEventListeners() {
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.onclick = () => switchView(btn.getAttribute('data-view'));
  });

  // Home buttons
  const homeRandomBtn = document.getElementById('homeGoRandomQuiz');
  if (homeRandomBtn) homeRandomBtn.onclick = () => startRandomQuiz();

  const homeTopicBtn = document.getElementById('homeGoTopicQuiz');
  if (homeTopicBtn) homeTopicBtn.onclick = () => switchView('topic-quiz');

  // Exam Navigation Buttons
  document.getElementById('examPrevBtn').onclick = goToPrevQuestion;
  document.getElementById('examNextBtn').onclick = goToNextQuestion;
  document.getElementById('examSubmitBtn').onclick = submitExam;
  
  const topSubmit = document.getElementById('topSubmitExamBtn');
  if (topSubmit) topSubmit.onclick = submitExam;

  // Exam Result Action Buttons
  const reviewBtn = document.getElementById('examReviewBtn');
  if (reviewBtn) {
    reviewBtn.onclick = () => {
      document.getElementById('quizMainCard').scrollIntoView({ behavior: 'smooth' });
    };
  }

  const retakeBtn = document.getElementById('examRetakeBtn');
  if (retakeBtn) {
    retakeBtn.onclick = () => startRandomQuiz();
  }

  // Back button
  document.getElementById('quizBackBtn').onclick = () => {
    switchView(state.activeView === 'random-quiz' && state.currentQuizList.length > 30 ? 'topic-quiz' : 'home');
  };

  // Custom Dropdowns
  function initCustomDropdown(wrapperId, hiddenInputId, onSelectCallback) {
    const wrapper = document.getElementById(wrapperId);
    if (!wrapper) return;
    const btn = wrapper.querySelector('.custom-dropdown-btn');
    const selectedText = wrapper.querySelector('.dropdown-selected-text');
    const hiddenInput = document.getElementById(hiddenInputId);
    const items = wrapper.querySelectorAll('.custom-dropdown-item');

    btn.onclick = (e) => {
      e.stopPropagation();
      document.querySelectorAll('.custom-dropdown').forEach(d => {
        if (d !== wrapper) d.classList.remove('open');
      });
      wrapper.classList.toggle('open');
    };

    items.forEach(item => {
      item.onclick = (e) => {
        e.stopPropagation();
        items.forEach(i => i.classList.remove('active'));
        item.classList.add('active');
        
        const val = item.getAttribute('data-val');
        const text = item.querySelector('span').textContent;
        
        selectedText.textContent = text;
        hiddenInput.value = val;
        wrapper.classList.remove('open');
        
        if (onSelectCallback) onSelectCallback(val);
      };
    });
  }

  initCustomDropdown('trackDropdown', 'filterTrackSelect', () => startRandomQuiz());
  initCustomDropdown('diffDropdown', 'filterDiffSelect', () => startRandomQuiz());

  document.addEventListener('click', () => {
    document.querySelectorAll('.custom-dropdown').forEach(d => d.classList.remove('open'));
  });

  const globalSearch = document.getElementById('globalSearchInput');
  if (globalSearch) {
    globalSearch.addEventListener('keydown', (e) => {
      if (e.key === 'Enter') {
        const query = globalSearch.value.trim().toLowerCase();
        if (!query) return;
        const matching = state.questions.filter(q => 
          q.question.toLowerCase().includes(query) ||
          q.topic.toLowerCase().includes(query) ||
          q.explanation.toLowerCase().includes(query)
        );
        if (matching.length > 0) {
          state.currentQuizList = matching;
          state.currentIndex = 0;
          state.isSubmitted = false;
          state.examUserAnswers = {};
          switchView('random-quiz');
          renderCurrentQuestion();
          renderPalette();
        } else {
          alert(`Không tìm thấy câu hỏi nào chứa từ khóa "${query}".`);
        }
      }
    });
  }

  const rightSidebar = document.getElementById('rightSidebar');
  document.getElementById('toggleRightPanelBtn').onclick = () => {
    rightSidebar.classList.toggle('collapsed');
  };
  document.getElementById('closeRightPanelBtn').onclick = () => {
    rightSidebar.classList.add('collapsed');
  };

  document.querySelectorAll('.panel-tab').forEach(tab => {
    tab.onclick = () => {
      document.querySelectorAll('.panel-tab').forEach(t => t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      tab.classList.add('active');
      const tabId = tab.getAttribute('data-tab');
      document.getElementById(tabId === 'cheatsheet' ? 'tabCheatsheet' : 'tabNotes').classList.add('active');
    };
  });

  // Keyboard Shortcuts in Exam Mode
  window.addEventListener('keydown', (e) => {
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;

    if (state.activeView === 'random-quiz') {
      if (['1', '2', '3', '4'].includes(e.key)) {
        selectExamOption(parseInt(e.key) - 1);
      } else if (e.key === 'ArrowRight' || e.key === 'Enter') {
        goToNextQuestion();
      } else if (e.key === 'ArrowLeft') {
        goToPrevQuestion();
      }
    }
  });

  window.addEventListener('keydown', (e) => {
    if ((e.key === '/' || (e.ctrlKey && e.key === 'k')) && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
      e.preventDefault();
      document.getElementById('globalSearchInput').focus();
    }
  });
}

document.addEventListener('DOMContentLoaded', initApp);
