/**
 * AI20K — Desktop Learning SPA Logic
 * Real Exam Mode: Answer all questions -> Navigate freely -> Submit at end -> Review score & explanations
 */

let state = {
  questions: [],
  currentQuizList: [],
  currentIndex: 0,
  quizMode: 'exam',         // 'exam' (Random Exam) or 'practice' (Day Practice)
  isSubmitted: false,       // Submitted state for exam mode
  examUserAnswers: {},      // { [qId]: chosenIdx }
  activeView: 'home'
};

function _practiceKey(day) {
  return 'midtermai_practice_' + (day || '').replace(/\s+/g, '_');
}

function saveState() {
  try {
    const toSave = {
      currentQuizListIds: state.currentQuizList.map(q => q.id),
      currentIndex: state.currentIndex,
      quizMode: state.quizMode,
      isSubmitted: state.isSubmitted,
      examUserAnswers: state.examUserAnswers,
      activeView: state.activeView,
      savedAt: Date.now()
    };
    if (state.quizMode === 'practice') {
      const day = state.currentQuizList[0]?.day || '';
      toSave.day = day;
      localStorage.setItem(_practiceKey(day), JSON.stringify(toSave));
      localStorage.setItem('midtermai_last', _practiceKey(day));
    } else {
      localStorage.setItem('midtermai_exam', JSON.stringify(toSave));
      localStorage.setItem('midtermai_last', 'midtermai_exam');
    }
  } catch (e) {}
}

function _loadAndApply(key, checkExpiry) {
  const raw = localStorage.getItem(key);
  if (!raw) return false;
  const saved = JSON.parse(raw);

  if (checkExpiry && Date.now() - saved.savedAt > 24 * 60 * 60 * 1000) {
    localStorage.removeItem(key);
    return false;
  }

  if (!saved.currentQuizListIds || saved.currentQuizListIds.length === 0) return false;

  const idMap = new Map(state.questions.map(q => [q.id, q]));
  const restored = saved.currentQuizListIds.map(id => idMap.get(id)).filter(Boolean);
  if (restored.length === 0) return false;

  state.currentQuizList = restored;
  state.currentIndex = saved.currentIndex || 0;
  state.quizMode = saved.quizMode || 'exam';
  state.isSubmitted = saved.isSubmitted || false;
  state.examUserAnswers = saved.examUserAnswers || {};
  state.activeView = saved.activeView || 'home';
  return true;
}

function restoreState() {
  try {
    const lastKey = localStorage.getItem('midtermai_last');
    if (!lastKey) return false;
    const isExam = lastKey === 'midtermai_exam';
    return _loadAndApply(lastKey, isExam);
  } catch (e) {
    return false;
  }
}

function restorePracticeForDay(day) {
  try {
    return _loadAndApply(_practiceKey(day), false);
  } catch (e) {
    return false;
  }
}

function clearSavedState() {
  try {
    localStorage.removeItem('midtermai_exam');
    localStorage.removeItem('midtermai_last');
  } catch (e) {}
}

function refreshIcons() {
  if (window.lucide) {
    lucide.createIcons();
  }
}

// Convert Markdown and Inline Code safely while preserving LaTeX Math
function formatContent(text) {
  if (!text) return '';
  
  // Protect math blocks ($...$ and $$...$$) from markdown replacement
  const mathBlocks = [];
  let placeholderText = text.replace(/(\$\$[\s\S]*?\$\$|\$[^\$\n]+?\$)/g, (match) => {
    mathBlocks.push(match);
    return `___MATH_BLOCK_${mathBlocks.length - 1}___`;
  });

  placeholderText = placeholderText
    .replace(/`([^`]+)`/g, '<code class="inline-code">$1</code>')
    .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
    .replace(/(?<!\w)\*(?!\s)([^*]+?)(?<!\s)\*(?!\w)/g, '<em>$1</em>')
    .replace(/\*/g, '&#42;');

  // Restore math blocks
  const restored = placeholderText.replace(/___MATH_BLOCK_(\d+)___/g, (_, idx) => {
    return mathBlocks[parseInt(idx, 10)];
  });

  return restored;
}

// Render KaTeX Math in a given DOM container
function renderMathInContainer(container) {
  if (!container) return;
  if (window.renderMathInElement) {
    try {
      window.renderMathInElement(container, {
        delimiters: [
          { left: '$$', right: '$$', display: true },
          { left: '$', right: '$', display: false },
          { left: '\\(', right: '\\)', display: false },
          { left: '\\[', right: '\\]', display: true }
        ],
        throwOnError: false,
        ignoredTags: ['script', 'noscript', 'style', 'textarea', 'pre']
      });
    } catch (e) {
      console.warn('KaTeX rendering error:', e);
    }
  }
}

// Local in-memory filter fallback
function getFilteredQuestions(track, diff, day) {
  let list = [...state.questions];
  if (track && track !== 'all') {
    list = list.filter(q => q.track && q.track.toLowerCase().includes(track.toLowerCase()));
  }
  if (diff && diff !== 'all') {
    list = list.filter(q => q.difficulty && q.difficulty.toLowerCase() === diff.toLowerCase());
  }
  if (day && day !== 'all') {
    const exact = list.filter(q => q.day && q.day.toLowerCase() === day.toLowerCase());
    if (exact.length > 0) {
      list = exact;
    } else {
      list = list.filter(q => q.day && q.day.toLowerCase().includes(day.toLowerCase()));
    }
  }
  return list;
}

async function initApp() {
  try {
    setupEventListeners();

    const candidates = [
      '/api/questions',
      '/static/data/questions.json',
      'static/data/questions.json',
      '/data/questions.json',
      'data/questions.json',
      './data/questions.json'
    ];

    for (const path of candidates) {
      try {
        const res = await fetch(path);
        if (res.ok) {
          const data = await res.json();
          const loaded = Array.isArray(data) ? data : (data.questions || []);
          if (loaded && loaded.length > 0) {
            state.questions = loaded;
            break;
          }
        }
      } catch (e) {
        // try next fallback path
      }
    }

    renderTopicsGrid();
    updateStatsDisplay();
    refreshIcons();
    renderMathInContainer(document.body);
    initPullToRefresh();
    initSwipeNavigation();

    if (restoreState() && state.currentQuizList.length > 0) {
      const modeBadge = document.getElementById('examModeBadge');
      if (state.quizMode === 'exam') {
        if (modeBadge) modeBadge.textContent = 'LUYỆN ĐỀ THI (NỘP BÀI ĐỂ XEM ĐÁP ÁN)';
      } else {
        const dayName = state.currentQuizList[0]?.day || '';
        if (modeBadge) modeBadge.textContent = `ÔN TẬP ${dayName.toUpperCase()} (PHẢN HỒI TỨC THÌ)`;
      }

      if (state.isSubmitted) {
        let correctCount = 0;
        state.currentQuizList.forEach(q => {
          if (state.examUserAnswers[q.id] === q.correct_index) correctCount++;
        });
        const total = state.currentQuizList.length;
        const percent = Math.round((correctCount / total) * 100);
        const banner = document.getElementById('examResultBanner');
        if (banner) {
          banner.classList.remove('hidden');
          document.getElementById('examScorePercent').textContent = `${percent}%`;
          document.getElementById('examResultTitle').textContent = percent >= 80 ? '🎉 Xuất Sắc!' : (percent >= 50 ? '👍 Đạt Yêu Cầu!' : '⚠️ Cần Ôn Tập Thêm!');
          document.getElementById('examResultDesc').textContent = `Bạn đã trả lời đúng ${correctCount}/${total} câu hỏi (${percent}%). Hãy xem lại chi tiết từng câu bên dưới.`;
        }
      }

      switchView(state.activeView);
      renderCurrentQuestion();
      renderPalette();
    }
  } catch (err) {
    console.error('Error initializing app:', err);
  }
}

// Start a Random Exam (30 questions)
async function startRandomQuiz(customTrack, customDiff) {
  const trackEl = document.getElementById('filterTrackSelect');
  const diffEl = document.getElementById('filterDiffSelect');
  const track = customTrack || (trackEl ? trackEl.value : 'all');
  const diff = customDiff || (diffEl ? diffEl.value : 'all');

  let qList = [];
  try {
    const res = await fetch(`/api/questions?track=${encodeURIComponent(track)}&difficulty=${encodeURIComponent(diff)}`);
    if (res.ok) {
      const data = await res.json();
      qList = data.questions || [];
    }
  } catch (e) {
    // API offline
  }

  // Fallback to local memory filter if API returned nothing
  if (qList.length === 0 && state.questions.length > 0) {
    qList = getFilteredQuestions(track, diff);
  }

  // Fallback to entire question set
  if (qList.length === 0 && state.questions.length > 0) {
    qList = [...state.questions];
  }

  // Pick 30 questions with balanced difficulty: 10 Easy + 10 Medium + 10 Hard
  const byDiff = { Easy: [], Medium: [], Hard: [] };
  for (const q of qList) {
    const d = q.difficulty || 'Medium';
    if (byDiff[d]) byDiff[d].push(q);
  }
  for (const arr of Object.values(byDiff)) arr.sort(() => Math.random() - 0.5);

  let selected = [
    ...byDiff.Easy.slice(0, 10),
    ...byDiff.Medium.slice(0, 10),
    ...byDiff.Hard.slice(0, 10)
  ];

  // Fill remaining slots if any difficulty group had fewer than 10
  if (selected.length < 30) {
    const usedIds = new Set(selected.map(q => q.id));
    const overflow = qList.filter(q => !usedIds.has(q.id)).sort(() => Math.random() - 0.5);
    selected = [...selected, ...overflow.slice(0, 30 - selected.length)];
  }

  selected.sort(() => Math.random() - 0.5);
  state.currentQuizList = selected.slice(0, 30);
  state.currentIndex = 0;
  state.quizMode = 'exam';
  state.isSubmitted = false;
  state.examUserAnswers = {};

  const banner = document.getElementById('examResultBanner');
  if (banner) banner.classList.add('hidden');
  const backText = document.getElementById('quizBackBtnText');
  if (backText) backText.textContent = 'Trang chủ';
  const modeBadge = document.getElementById('examModeBadge');
  if (modeBadge) modeBadge.textContent = 'LUYỆN ĐỀ THI (NỘP BÀI ĐỂ XEM ĐÁP ÁN)';

  switchView('random-quiz');
  renderCurrentQuestion();
  renderPalette();
  saveState();
}

// Start a Day-specific practice (45 questions with INSTANT FEEDBACK)
async function startDayQuiz(dayName, trackName) {
  // Restore saved progress for this day if available
  if (restorePracticeForDay(dayName)) {
    const banner = document.getElementById('examResultBanner');
    if (banner) banner.classList.add('hidden');
    const backText = document.getElementById('quizBackBtnText');
    if (backText) backText.textContent = 'Danh sách Day';
    const modeBadge = document.getElementById('examModeBadge');
    if (modeBadge) modeBadge.textContent = `ÔN TẬP ${dayName.toUpperCase()} (PHẢN HỒI TỨC THÌ)`;

    switchView('random-quiz');
    renderCurrentQuestion();
    renderPalette();
    return;
  }

  let qList = [];
  try {
    let url = `/api/questions?day=${encodeURIComponent(dayName)}`;
    if (trackName && trackName !== 'all') {
      url += `&track=${encodeURIComponent(trackName)}`;
    }
    const res = await fetch(url);
    if (res.ok) {
      const data = await res.json();
      qList = data.questions || [];
    }
  } catch (e) {
    // API offline
  }

  if (qList.length === 0 && state.questions.length > 0) {
    qList = getFilteredQuestions(trackName || 'all', 'all', dayName);
  }

  state.currentQuizList = qList;
  state.currentIndex = 0;
  state.quizMode = 'practice';
  state.isSubmitted = false;
  state.examUserAnswers = {};

  const banner = document.getElementById('examResultBanner');
  if (banner) banner.classList.add('hidden');
  const backText = document.getElementById('quizBackBtnText');
  if (backText) backText.textContent = 'Danh sách Day';
  const modeBadge = document.getElementById('examModeBadge');
  if (modeBadge) modeBadge.textContent = `ÔN TẬP ${dayName.toUpperCase()} (PHẢN HỒI TỨC THÌ)`;

  switchView('random-quiz');
  renderCurrentQuestion();
  renderPalette();
  saveState();
}

function togglePaletteCollapse() {
  const container = document.getElementById('examPaletteContainer');
  const toggleText = document.getElementById('paletteToggleText');
  if (!container) return;
  const isCollapsed = container.classList.toggle('collapsed');
  if (toggleText) {
    toggleText.textContent = isCollapsed ? 'Hiện bảng' : 'Ẩn bảng';
  }
}

// Render Palette Grid (1 to N)
function renderPalette() {
  const container = document.getElementById('paletteGrid');
  if (!container) return;
  container.innerHTML = '';

  const isPractice = (state.quizMode === 'practice');
  const isExamReview = (state.quizMode === 'exam' && state.isSubmitted);
  const showFeedback = isPractice || isExamReview;

  state.currentQuizList.forEach((q, idx) => {
    const item = document.createElement('div');
    item.className = 'palette-item';
    item.textContent = idx + 1;
    
    if (idx === state.currentIndex) {
      item.classList.add('current');
    }

    const chosen = state.examUserAnswers[q.id];
    if (chosen !== undefined) {
      if (showFeedback) {
        if (chosen === q.correct_index) {
          item.classList.add('correct');
        } else {
          item.classList.add('incorrect');
        }
      } else {
        item.classList.add('answered');
      }
    }

    item.onclick = () => {
      state.currentIndex = idx;
      saveState();
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

  const isExam = state.quizMode === 'exam';

  const trackBadge = document.getElementById('qTrackBadge');
  const dayBadge = document.getElementById('qDayBadge');
  const diffBadge = document.getElementById('qDiffBadge');

  trackBadge.textContent = q.track;
  dayBadge.textContent = q.day;
  diffBadge.textContent = q.difficulty;
  diffBadge.className = `badge-editorial badge-editorial-diff`;

  // Hide track/day/difficulty badges in exam mode — reveal only in practice mode
  trackBadge.classList.toggle('hidden', isExam);
  dayBadge.classList.toggle('hidden', isExam);
  diffBadge.classList.toggle('hidden', isExam);

  document.getElementById('qQuestionText').innerHTML = formatContent(q.question.replace(/^\[.*?\]\s*/, ''));
  document.getElementById('quizProgressText').textContent = `${currNum}/${total}`;

  const modeBadge = document.getElementById('examModeBadge');
  if (modeBadge && isExam) {
    modeBadge.textContent = 'LUYỆN ĐỀ';
  }

  // Top Submit Button: Only shown in Exam Mode before submitting
  const topSubmitBtn = document.getElementById('topSubmitExamBtn');
  if (topSubmitBtn) {
    const showSubmit = (state.quizMode === 'exam' && !state.isSubmitted);
    topSubmitBtn.classList.toggle('hidden', !showSubmit);
  }

  // Determine whether to reveal answer correctness and explanation
  const isPractice = (state.quizMode === 'practice');
  const isExamReview = (state.quizMode === 'exam' && state.isSubmitted);
  const chosenIdx = state.examUserAnswers[q.id];
  const hasAnswered = (chosenIdx !== undefined);
  const showFeedback = isPractice ? hasAnswered : isExamReview;
  const isOptionClickable = isPractice ? !hasAnswered : !state.isSubmitted;

  // Render Options
  const container = document.getElementById('optionsContainer');
  container.innerHTML = '';

  q.options.forEach((optText, idx) => {
    const row = document.createElement('div');
    row.className = 'sleek-option-row';

    if (showFeedback) {
      if (idx === q.correct_index) {
        row.classList.add('correct');
      } else if (chosenIdx === idx) {
        row.classList.add('incorrect');
      }
    } else if (chosenIdx === idx) {
      row.classList.add('selected');
    }

    row.innerHTML = `
      <div class="radio-circle">
        <div class="radio-circle-inner"></div>
      </div>
      <div class="option-row-text"><strong class="option-letter mr-1">${String.fromCharCode(65 + idx)}.</strong> ${formatContent(optText)}</div>
    `;

    if (isOptionClickable) {
      row.onclick = () => selectExamOption(idx);
    }

    container.appendChild(row);
  });

  // Explanation Box handling:
  // - Practice Mode: Revealed immediately once answered
  // - Exam Mode: Revealed ONLY after submitting exam
  const expBox = document.getElementById('explanationBox');
  if (showFeedback) {
    expBox.classList.remove('hidden');
    const isCorrect = (chosenIdx === q.correct_index);
    const correctLetter = String.fromCharCode(65 + q.correct_index);
    const statusText = isCorrect 
      ? '✅ Chính xác! Bạn đã chọn đúng đáp án.' 
      : `❌ Chưa chính xác! Đáp án đúng là <strong>${correctLetter}</strong>.`;
    
    document.getElementById('explanationStatus').innerHTML = statusText;
    document.getElementById('explanationContent').innerHTML = formatContent(q.explanation);
    
    const slideRef = document.getElementById('slideRefLink');
    if (slideRef) {
      slideRef.textContent = q.slide_ref || 'Slide bài giảng';
    }
  } else {
    expBox.classList.add('hidden');
  }

  // Navigation Buttons
  const prevBtn = document.getElementById('examPrevBtn');
  const nextBtn = document.getElementById('examNextBtn');

  if (prevBtn) {
    prevBtn.disabled = (state.currentIndex === 0);
    prevBtn.style.opacity = (state.currentIndex === 0) ? '0.4' : '1';
  }

  if (nextBtn) {
    const isLast = state.currentIndex === total - 1;
    const isExamSubmittable = isLast && state.quizMode === 'exam' && !state.isSubmitted;
    if (isExamSubmittable) {
      nextBtn.textContent = 'Nộp bài ✓';
      nextBtn.classList.add('btn-nav-submit');
    } else {
      nextBtn.textContent = isLast ? 'Quay lại câu 1' : 'Câu tiếp theo →';
      nextBtn.classList.remove('btn-nav-submit');
    }
  }

  renderPalette();
  refreshIcons();

  // Render LaTeX math formulas across the question card
  const quizView = document.getElementById('viewRandomQuiz');
  if (quizView) {
    renderMathInContainer(quizView);
  }
}

function selectExamOption(idx) {
  if (state.quizMode === 'exam' && state.isSubmitted) return;
  if (state.quizMode === 'practice' && state.examUserAnswers[state.currentQuizList[state.currentIndex]?.id] !== undefined) return;
  
  const q = state.currentQuizList[state.currentIndex];
  if (!q) return;

  state.examUserAnswers[q.id] = idx;
  saveState();
  renderCurrentQuestion();
}

function goToPrevQuestion() {
  if (state.currentIndex > 0) {
    state.currentIndex--;
    saveState();
    renderCurrentQuestion();
  }
}

function goToNextQuestion() {
  const total = state.currentQuizList.length;
  const isLast = state.currentIndex === total - 1;
  if (isLast && state.quizMode === 'exam' && !state.isSubmitted) {
    openSubmitModal();
    return;
  }
  if (state.currentIndex < total - 1) {
    state.currentIndex++;
  } else {
    state.currentIndex = 0;
  }
  saveState();
  renderCurrentQuestion();
}

function openSubmitModal() {
  const total = (state.currentQuizList && state.currentQuizList.length) ? state.currentQuizList.length : 30;
  const answeredCount = Object.keys(state.examUserAnswers).length;
  const unansweredCount = Math.max(0, total - answeredCount);

  const modal = document.getElementById('submitConfirmModal');
  if (!modal) {
    console.error('Modal element #submitConfirmModal not found');
    return;
  }

  const iconBadge = document.getElementById('modalIconBadge');
  const answeredEl = document.getElementById('modalAnsweredCount');
  const unansweredEl = document.getElementById('modalUnansweredCount');
  const unansweredBox = document.getElementById('modalUnansweredBox');
  const messageEl = document.getElementById('modalMessageText');

  if (answeredEl) answeredEl.textContent = `${answeredCount} / ${total}`;
  if (unansweredEl) unansweredEl.textContent = `${unansweredCount}`;

  if (unansweredCount > 0) {
    if (iconBadge) {
      iconBadge.className = 'modal-icon-badge warning';
      iconBadge.innerHTML = '<i data-lucide="alert-triangle"></i>';
    }
    if (unansweredBox) unansweredBox.className = 'modal-stat-box unanswered-warning';
    if (messageEl) {
      messageEl.innerHTML = `Bạn mới làm <strong>${answeredCount}/${total} câu</strong> (còn <strong>${unansweredCount} câu</strong> chưa trả lời). Bạn có chắc chắn muốn nộp bài thi ngay bây giờ không?`;
    }
  } else {
    if (iconBadge) {
      iconBadge.className = 'modal-icon-badge success';
      iconBadge.innerHTML = '<i data-lucide="check-circle-2"></i>';
    }
    if (unansweredBox) unansweredBox.className = 'modal-stat-box unanswered-success';
    if (messageEl) {
      messageEl.innerHTML = `Tuyệt vời! Bạn đã hoàn thành toàn bộ <strong>${total}/${total} câu hỏi</strong>. Nhấn <strong>"Nộp bài ngay"</strong> để xem kết quả điểm số và phân tích đáp án chi tiết.`;
    }
  }

  modal.classList.remove('hidden');
  modal.style.display = 'flex';
  refreshIcons();
}

function closeSubmitModal() {
  const modal = document.getElementById('submitConfirmModal');
  if (modal) {
    modal.classList.add('hidden');
    modal.style.display = 'none';
  }
}

function confirmSubmitAndClose() {
  closeSubmitModal();
  processExamSubmission();
}

// Attach to window so inline HTML onclick and external callers always work
window.openSubmitModal = openSubmitModal;
window.closeSubmitModal = closeSubmitModal;
window.confirmSubmitAndClose = confirmSubmitAndClose;

function processExamSubmission() {
  const total = state.currentQuizList.length;
  if (total === 0) return;

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
  saveState();
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
        track: q.track,
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
        <div class="topic-card card" onclick="startDayQuiz('${dayName}', '${dayInfo.track}')">
          <div class="topic-card-header">
            <span class="badge-editorial badge-editorial-day">${dayName}</span>
            <span class="text-xs text-muted font-bold">${dayInfo.count} câu hỏi</span>
          </div>
          <h4 class="topic-card-name font-editorial">${formatContent(dayInfo.topic)}</h4>
          <div class="topic-card-progress mt-2">
            <div class="flex-between mt-2">
              <span class="text-xs text-muted">Trọn bộ 45 câu</span>
              <span class="text-xs text-terracotta font-bold topic-card-cta">Luyện tập Day này ➔</span>
            </div>
          </div>
        </div>
      `;
    }

    html += `</div></div>`;
  }

  container.innerHTML = html;
  renderMathInContainer(container);
}

function updateStatsDisplay() {
  document.getElementById('headerCompletedCount').textContent = `Tổng kho: ${state.questions.length} câu`;
}

function openMobileSidebar() {
  const sidebar = document.getElementById('sidebarLeft');
  const overlay = document.getElementById('mobileSidebarOverlay');
  if (sidebar) sidebar.classList.add('mobile-open');
  if (overlay) overlay.classList.remove('hidden');
}

function closeMobileSidebar() {
  const sidebar = document.getElementById('sidebarLeft');
  const overlay = document.getElementById('mobileSidebarOverlay');
  if (sidebar) sidebar.classList.remove('mobile-open');
  if (overlay) overlay.classList.add('hidden');
}

function switchView(viewId) {
  state.activeView = viewId;
  document.querySelectorAll('.view-panel').forEach(p => p.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.mobile-nav-item[data-view]').forEach(b => b.classList.remove('active'));

  // Day practice lives in the quiz panel but should highlight the "Ôn tập theo Day" nav
  const navViewId = (viewId === 'random-quiz' && state.quizMode === 'practice') ? 'topic-quiz' : viewId;

  const activeBtn = document.querySelector(`.nav-item[data-view="${navViewId}"]`);
  if (activeBtn) activeBtn.classList.add('active');

  const activeMobileBtn = document.querySelector(`.mobile-nav-item[data-view="${navViewId}"]`);
  if (activeMobileBtn) activeMobileBtn.classList.add('active');

  closeMobileSidebar();

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
  document.getElementById('currentViewTitle').textContent = titles[navViewId] || '';
  
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
    btn.onclick = () => {
      const view = btn.getAttribute('data-view');
      if (view === 'random-quiz') startRandomQuiz(); else switchView(view);
    };
  });

  document.querySelectorAll('.mobile-nav-item[data-view]').forEach(btn => {
    btn.onclick = () => {
      const view = btn.getAttribute('data-view');
      if (view === 'random-quiz') startRandomQuiz(); else switchView(view);
    };
  });

  // Mobile drawer buttons
  const mobileFilterNavBtn = document.getElementById('mobileFilterNavBtn');
  if (mobileFilterNavBtn) mobileFilterNavBtn.onclick = openMobileSidebar;

  const closeMobileSidebarBtn = document.getElementById('closeMobileSidebarBtn');
  if (closeMobileSidebarBtn) closeMobileSidebarBtn.onclick = closeMobileSidebar;

  const mobileSidebarOverlay = document.getElementById('mobileSidebarOverlay');
  if (mobileSidebarOverlay) mobileSidebarOverlay.onclick = closeMobileSidebar;

  // Home buttons
  const homeRandomBtn = document.getElementById('homeGoRandomQuiz');
  if (homeRandomBtn) homeRandomBtn.onclick = () => startRandomQuiz();

  const homeTopicBtn = document.getElementById('homeGoTopicQuiz');
  if (homeTopicBtn) homeTopicBtn.onclick = () => switchView('topic-quiz');

  // Exam Navigation Buttons
  document.getElementById('examPrevBtn').onclick = goToPrevQuestion;
  document.getElementById('examNextBtn').onclick = goToNextQuestion;
  
  const topSubmit = document.getElementById('topSubmitExamBtn');
  if (topSubmit) topSubmit.onclick = openSubmitModal;

  // Palette collapse toggle — single handler on the full header row
  const paletteHeaderToggle = document.getElementById('paletteHeaderToggle');
  if (paletteHeaderToggle) {
    paletteHeaderToggle.addEventListener('click', togglePaletteCollapse);
  }

  // Submit Modal Actions
  const submitModal = document.getElementById('submitConfirmModal');
  const closeSubmitModalBtn = document.getElementById('closeSubmitModalBtn');
  const cancelSubmitBtn = document.getElementById('cancelSubmitBtn');
  const confirmSubmitBtn = document.getElementById('confirmSubmitBtn');

  if (closeSubmitModalBtn) closeSubmitModalBtn.onclick = closeSubmitModal;
  if (cancelSubmitBtn) cancelSubmitBtn.onclick = closeSubmitModal;
  if (confirmSubmitBtn) {
    confirmSubmitBtn.onclick = () => {
      closeSubmitModal();
      processExamSubmission();
    };
  }

  if (submitModal) {
    submitModal.onclick = (e) => {
      if (e.target === submitModal) {
        closeSubmitModal();
      }
    };
  }

  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && submitModal && !submitModal.classList.contains('hidden')) {
      closeSubmitModal();
    }
  });

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

  // Back button — only clear exam state, practice persists
  document.getElementById('quizBackBtn').onclick = () => {
    if (state.quizMode === 'exam') clearSavedState();
    switchView(state.quizMode === 'practice' ? 'topic-quiz' : 'home');
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

// =========================================================
// SWIPE TO NAVIGATE (mobile only) — with live drag + animation
// =========================================================
function initSwipeNavigation() {
  const workspace = document.querySelector('.content-workspace');
  if (!workspace) return;

  const MIN_SWIPE_X = 50;
  const MAX_SWIPE_Y = 80;

  let startX = 0, startY = 0, tracking = false, dragging = false;

  function card() { return document.getElementById('questionCard'); }

  function resetCard() {
    const c = card();
    if (!c) return;
    c.style.transition = '';
    c.style.transform = '';
    c.style.opacity = '';
  }

  function snapBack() {
    const c = card();
    if (!c) return;
    c.style.transition = 'transform 0.3s cubic-bezier(0.34,1.56,0.64,1), opacity 0.2s ease';
    c.style.transform = 'translateX(0)';
    c.style.opacity = '1';
    c.addEventListener('transitionend', resetCard, { once: true });
  }

  function slideAndNavigate(direction, navigate) {
    const c = card();
    if (!c) { navigate(); return; }

    const exitX  = direction === 'left' ? '-110%' : '110%';
    const enterX = direction === 'left' ?  '110%' : '-110%';

    // Slide current card out
    c.style.transition = 'transform 0.18s ease-in, opacity 0.18s ease-in';
    c.style.transform  = `translateX(${exitX})`;
    c.style.opacity    = '0';

    setTimeout(() => {
      // Position new card on opposite side (invisible)
      c.style.transition = 'none';
      c.style.transform  = `translateX(${enterX})`;
      c.style.opacity    = '0';

      navigate(); // update content

      // Slide new card in
      requestAnimationFrame(() => requestAnimationFrame(() => {
        c.style.transition = 'transform 0.22s ease-out, opacity 0.18s ease-out';
        c.style.transform  = 'translateX(0)';
        c.style.opacity    = '1';
        c.addEventListener('transitionend', resetCard, { once: true });
      }));
    }, 185);
  }

  workspace.addEventListener('touchstart', (e) => {
    if (state.activeView !== 'random-quiz') return;
    startX = e.touches[0].clientX;
    startY = e.touches[0].clientY;
    tracking = true;
    dragging = false;
    const c = card();
    if (c) c.style.transition = 'none';
  }, { passive: true });

  workspace.addEventListener('touchmove', (e) => {
    if (!tracking) return;
    const dx = e.touches[0].clientX - startX;
    const dy = e.touches[0].clientY - startY;

    if (!dragging) {
      if (Math.abs(dx) > 8 && Math.abs(dx) > Math.abs(dy)) dragging = true;
      else if (Math.abs(dy) > 8) { tracking = false; return; }
      else return;
    }

    e.preventDefault();
    const c = card();
    if (c) {
      c.style.transform = `translateX(${dx}px)`;
      c.style.opacity   = String(Math.max(0.4, 1 - Math.abs(dx) / 260));
    }
  }, { passive: false });

  workspace.addEventListener('touchcancel', () => {
    if (dragging) snapBack();
    tracking = false;
    dragging = false;
  }, { passive: true });

  workspace.addEventListener('touchend', (e) => {
    if (!tracking) return;
    tracking = false;
    if (state.activeView !== 'random-quiz') { if (dragging) snapBack(); dragging = false; return; }

    const dx = e.changedTouches[0].clientX - startX;
    const dy = e.changedTouches[0].clientY - startY;
    const wasDragging = dragging;
    dragging = false;

    if (!wasDragging || Math.abs(dx) < MIN_SWIPE_X || Math.abs(dy) > MAX_SWIPE_Y) {
      if (wasDragging) snapBack();
      return;
    }

    if (dx < 0) {
      slideAndNavigate('left', goToNextQuestion);
    } else {
      if (state.currentIndex > 0) {
        slideAndNavigate('right', goToPrevQuestion);
      } else {
        snapBack();
      }
    }
  }, { passive: true });
}

// =========================================================
// PULL-TO-REFRESH (mobile only)
// =========================================================
function initPullToRefresh() {
  if (window.innerWidth > 768) return;

  const workspace = document.querySelector('.content-workspace');
  if (!workspace) return;

  // Inject indicator at top of workspace
  const indicator = document.createElement('div');
  indicator.id = 'ptrIndicator';
  indicator.innerHTML = `
    <div class="ptr-icon-wrap">
      <svg class="ptr-arrow" viewBox="0 0 24 24" width="22" height="22" fill="none"
           stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
        <polyline points="1 4 1 10 7 10"></polyline>
        <path d="M3.51 15a9 9 0 1 0 .49-3.51"></path>
      </svg>
      <svg class="ptr-spinner hidden" viewBox="0 0 24 24" width="22" height="22" fill="none"
           stroke="currentColor" stroke-width="2.5" stroke-linecap="round">
        <circle cx="12" cy="12" r="10" stroke-dasharray="50" stroke-dashoffset="15"/>
      </svg>
    </div>
    <span class="ptr-text">Kéo xuống để làm mới</span>
  `;
  workspace.prepend(indicator);

  // Toast element
  const toast = document.createElement('div');
  toast.className = 'ptr-toast';
  document.body.appendChild(toast);

  function showToast(msg) {
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 2200);
  }

  const THRESHOLD = 75;
  let startY = 0;
  let currentPull = 0;
  let isPulling = false;
  let isRefreshing = false;

  workspace.addEventListener('touchstart', (e) => {
    if (workspace.scrollTop === 0 && !isRefreshing) {
      startY = e.touches[0].clientY;
      isPulling = true;
      currentPull = 0;
      indicator.style.transition = '';
    }
  }, { passive: true });

  workspace.addEventListener('touchmove', (e) => {
    if (!isPulling || isRefreshing) return;
    const dy = e.touches[0].clientY - startY;
    if (dy <= 0) { currentPull = 0; return; }

    // Dampen so it feels elastic (square-root damping)
    currentPull = Math.min(dy * 0.55, THRESHOLD * 1.6);

    const progress = Math.min(currentPull / THRESHOLD, 1);

    indicator.style.height = currentPull + 'px';
    indicator.style.opacity = progress;

    const arrow = indicator.querySelector('.ptr-arrow');
    if (arrow) arrow.style.transform = `rotate(${progress * 270}deg)`;

    const textEl = indicator.querySelector('.ptr-text');
    if (textEl) textEl.textContent = progress >= 1 ? 'Thả để làm mới ↑' : 'Kéo xuống để làm mới';
  }, { passive: true });

  workspace.addEventListener('touchend', async () => {
    if (!isPulling) return;
    isPulling = false;

    if (currentPull >= THRESHOLD) {
      isRefreshing = true;

      // Show spinner
      const arrow = indicator.querySelector('.ptr-arrow');
      const spinner = indicator.querySelector('.ptr-spinner');
      const textEl = indicator.querySelector('.ptr-text');

      if (arrow) { arrow.style.transform = ''; arrow.classList.add('hidden'); }
      if (spinner) spinner.classList.remove('hidden');
      if (textEl) textEl.textContent = 'Đang làm mới...';

      indicator.style.transition = 'height 0.2s ease';
      indicator.style.height = '64px';
      indicator.style.opacity = '1';

      // Reload data
      await ptrRefreshData();

      showToast('✓ Đã làm mới dữ liệu');

      // Collapse
      indicator.style.transition = 'height 0.3s ease, opacity 0.3s ease';
      indicator.style.height = '0px';
      indicator.style.opacity = '0';

      setTimeout(() => {
        indicator.style.transition = '';
        if (arrow) arrow.classList.remove('hidden');
        if (spinner) spinner.classList.add('hidden');
        if (textEl) textEl.textContent = 'Kéo xuống để làm mới';
        isRefreshing = false;
        currentPull = 0;
      }, 300);

    } else {
      // Snap back without refresh
      indicator.style.transition = 'height 0.22s ease, opacity 0.22s ease';
      indicator.style.height = '0px';
      indicator.style.opacity = '0';
      setTimeout(() => { indicator.style.transition = ''; }, 220);
      currentPull = 0;
    }
  }, { passive: true });
}

async function ptrRefreshData() {
  const candidates = [
    '/api/questions',
    '/static/data/questions.json',
    'static/data/questions.json',
    '/data/questions.json',
    'data/questions.json'
  ];
  for (const path of candidates) {
    try {
      const res = await fetch(path + (path.includes('?') ? '&' : '?') + '_t=' + Date.now());
      if (res.ok) {
        const data = await res.json();
        const loaded = Array.isArray(data) ? data : (data.questions || []);
        if (loaded && loaded.length > 0) {
          state.questions = loaded;
          break;
        }
      }
    } catch (e) { /* try next */ }
  }

  renderTopicsGrid();
  updateStatsDisplay();
  refreshIcons();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initApp);
} else {
  initApp();
}
