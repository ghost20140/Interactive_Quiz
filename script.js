class QuizManager {
    constructor() {
      this.currentQuestionIndex = 0;
      this.score = 0;
      this.questions = [];
      this.isAnswered = false;
  
      this.$ = (id) => document.getElementById(id);
  
      this.refs = {
        chapterSelect: this.$("chapterSelect"),
        questionCount: this.$("questionCount"),
        generateBtn: this.$("generateBtn"),
        downloadJson: this.$("downloadJson"),
        loading: this.$("loading"),
        questionText: this.$("questionText"),
        options: this.$("options"),
        nextBtn: this.$("nextBtn"),
        progressFill: this.$("progressFill"),
      };
  
      this.bindEvents();
      this.fetchChapters();
    }
  
    bindEvents() {
      this.refs.generateBtn.addEventListener("click", () => this.generate());
      this.refs.nextBtn.addEventListener("click", () => this.next());
    }
  
    async fetchChapters() {
      try {
        const res = await fetch("/api/chapters");
        const data = await res.json();
        const chapters = data.chapters || [];
        this.refs.chapterSelect.innerHTML = chapters
          .map((c) => `<option value="${c.id}">${c.title}</option>`)
          .join("");
      } catch (e) {
        console.error(e);
        this.refs.chapterSelect.innerHTML =
          `<option value="">(no chapters found)</option>`;
      }
    }
  
    setLoading(show) {
      this.refs.loading.style.display = show ? "flex" : "none";
    }
  
    setProgress() {
      const pct = this.questions.length
        ? Math.round((this.currentQuestionIndex / this.questions.length) * 100)
        : 0;
      this.refs.progressFill.style.width = `${pct}%`;
    }
  
    renderQuestion() {
      const q = this.questions[this.currentQuestionIndex];
      if (!q) return;
  
      this.refs.questionText.textContent = q.question;
      this.refs.options.innerHTML = q.options
        .map(
          (opt, idx) => `<button class="option" data-idx="${idx}">${opt}</button>`
        )
        .join("");
  
      [...this.refs.options.querySelectorAll(".option")].forEach((btn) => {
        btn.addEventListener("click", () => this.answer(parseInt(btn.dataset.idx)));
      });
  
      this.refs.nextBtn.disabled = true;
      this.isAnswered = false;
      this.setProgress();
    }
  
    answer(idx) {
      if (this.isAnswered) return;
      this.isAnswered = true;
  
      const q = this.questions[this.currentQuestionIndex];
      const correct = q.correct;
  
      [...this.refs.options.querySelectorAll(".option")].forEach((btn) => {
        const i = parseInt(btn.dataset.idx);
        if (i === correct) btn.classList.add("correct");
        if (i === idx && idx !== correct) btn.classList.add("incorrect");
        btn.disabled = true;
      });
  
      if (idx === correct) this.score += 1;
      this.refs.nextBtn.disabled = false;
    }
  
    next() {
      this.currentQuestionIndex += 1;
      if (this.currentQuestionIndex >= this.questions.length) {
        this.finish();
      } else {
        this.renderQuestion();
      }
    }
  
    finish() {
      const total = this.questions.length;
      const pct = Math.round((this.score / total) * 100);
      this.refs.questionText.textContent =
        `Done! You scored ${this.score}/${total} (${pct}%).`;
      this.refs.options.innerHTML = "";
      this.refs.nextBtn.disabled = true;
  
      // Enable JSON download of the generated quiz
      const blob = new Blob(
        [JSON.stringify({ questions: this.questions }, null, 2)],
        { type: "application/json" }
      );
      const url = URL.createObjectURL(blob);
      this.refs.downloadJson.href = url;
      this.refs.downloadJson.style.display = "inline-block";
    }
  
    async generate() {
      const chapter_id = this.refs.chapterSelect.value;
      const num_questions = parseInt(this.refs.questionCount.value || "5", 10);
      if (!chapter_id) {
        alert("Please select a chapter");
        return;
      }
  
      this.setLoading(true);
      try {
        const res = await fetch("/api/generate-questions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ chapter_id, num_questions }),
        });
  
        let data;
        try { data = await res.json(); } catch { data = null; }
  
        if (!res.ok) {
          const msg = (data && (data.error || data.message)) || `HTTP ${res.status}`;
          throw new Error(msg);
        }
        if (!data.success) throw new Error(data.error || "Unknown error");
  
        this.questions = data.questions || [];
        this.score = 0;
        this.currentQuestionIndex = 0;
        this.refs.downloadJson.style.display = "none";
  
        this.renderQuestion();
      } catch (e) {
        console.error(e);
        this.refs.questionText.textContent = `Error: ${e.message}`;
        this.refs.options.innerHTML =
          '<button class="btn" onclick="location.reload()">Reload</button>';
      } finally {
        this.setLoading(false);
      }
    }
  }
  
  window.addEventListener("DOMContentLoaded", () => new QuizManager());
  