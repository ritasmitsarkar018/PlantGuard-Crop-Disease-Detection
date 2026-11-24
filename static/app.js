// PlantGuard AI - Interactive Application Logic with Dual Theme & Demo Samples

document.addEventListener("DOMContentLoaded", () => {
  // 1. THEME SWITCHER (Dark Midnight vs. Light Daylight)
  const themeToggle = document.getElementById("theme-toggle");
  const htmlElement = document.documentElement;

  // Initialize theme from localStorage or system preference
  const savedTheme = localStorage.getItem("plantguard_theme");
  if (savedTheme) {
    htmlElement.setAttribute("data-theme", savedTheme);
  } else {
    // Default to dark theme for high-tech aesthetic
    htmlElement.setAttribute("data-theme", "dark");
  }

  if (themeToggle) {
    themeToggle.addEventListener("click", () => {
      const currentTheme = htmlElement.getAttribute("data-theme") || "dark";
      const newTheme = currentTheme === "dark" ? "light" : "dark";
      htmlElement.setAttribute("data-theme", newTheme);
      localStorage.setItem("plantguard_theme", newTheme);
    });
  }

  // 2. NAVIGATION TABS
  const navTabs = document.querySelectorAll(".nav-tab");
  const tabViews = document.querySelectorAll(".tab-view");

  navTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const targetId = tab.getAttribute("data-tab");
      navTabs.forEach(t => t.classList.remove("active"));
      tabViews.forEach(v => v.classList.remove("active"));

      tab.classList.add("active");
      const targetView = document.getElementById(targetId);
      if (targetView) targetView.classList.add("active");

      // Load specific tab data when activated
      if (targetId === "encyclopedia-tab") loadEncyclopedia();
      if (targetId === "history-tab") loadHistoryAndStats();
    });
  });

  // State
  let currentFile = null;
  let currentGradcamData = { original: "", heatmap: "", overlay: "" };
  let cameraStream = null;
  let allDiseases = {};

  // DOM Elements
  const dropzoneArea = document.getElementById("dropzone-area");
  const fileInput = document.getElementById("file-input");
  const previewBox = document.getElementById("preview-box");
  const imagePreview = document.getElementById("image-preview");
  const btnRemoveImage = document.getElementById("btn-remove-image");
  const btnAnalyze = document.getElementById("btn-analyze");
  const scanNotes = document.getElementById("scan-notes");
  const cropSelector = document.getElementById("crop-selector");
  const plantPills = document.querySelectorAll(".btn-plant-pill");
  const activePlantIndicator = document.getElementById("active-plant-indicator");

  function selectPlant(cropName) {
    if (cropSelector) cropSelector.value = cropName;
    plantPills.forEach(p => {
      if (p.getAttribute("data-crop").toLowerCase() === cropName.toLowerCase()) {
        p.classList.add("active");
      } else {
        p.classList.remove("active");
      }
    });

    if (activePlantIndicator) {
      if (cropName.toLowerCase() === "auto") {
        activePlantIndicator.textContent = "Auto-Detect (All 38 Classes)";
      } else {
        activePlantIndicator.textContent = `Target: ${cropName} (Filtering ${cropName} Diseases)`;
      }
    }

    // Auto re-analyze if an image is already staged
    if (currentFile && !btnAnalyze.disabled) {
      btnAnalyze.click();
    }
  }

  plantPills.forEach(pill => {
    pill.addEventListener("click", () => {
      const crop = pill.getAttribute("data-crop");
      selectPlant(crop);
    });
  });

  const toggleUpload = document.getElementById("toggle-upload");
  const toggleCamera = document.getElementById("toggle-camera");
  const cameraArea = document.getElementById("camera-area");
  const webcamVideo = document.getElementById("webcam-video");
  const cameraCanvas = document.getElementById("camera-canvas");
  const btnCapture = document.getElementById("btn-capture");
  const btnRetake = document.getElementById("btn-retake");

  const resultsPlaceholder = document.getElementById("results-placeholder");
  const resultsContent = document.getElementById("results-content");

  // Results elements
  const resCropBadge = document.getElementById("res-crop-badge");
  const resSeverityBadge = document.getElementById("res-severity-badge");
  const resDiseaseName = document.getElementById("res-disease-name");
  const radialProgress = document.getElementById("radial-progress");
  const resConfidenceText = document.getElementById("res-confidence-text");
  const gradcamImage = document.getElementById("gradcam-image");
  const topPredictionsList = document.getElementById("top-predictions-list");
  const resSymptoms = document.getElementById("res-symptoms");
  const resOrganic = document.getElementById("res-organic");
  const resChemical = document.getElementById("res-chemical");
  const resPrevention = document.getElementById("res-prevention");
  const btnPrintReport = document.getElementById("btn-print-report");

  // 3. QUICK DEMO SAMPLES
  const sampleButtons = document.querySelectorAll(".btn-sample");
  sampleButtons.forEach(btn => {
    btn.addEventListener("click", async () => {
      const sampleKey = btn.getAttribute("data-sample");
      sampleButtons.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");

      // Stop camera if running
      stopCamera();
      toggleUpload.classList.add("active");
      toggleCamera.classList.remove("active");
      dropzoneArea.classList.remove("hidden");
      cameraArea.classList.add("hidden");

      try {
        const sampleUrl = `/static/samples/sample_${sampleKey}.jpg`;
        const res = await fetch(sampleUrl);
        if (!res.ok) throw new Error("Could not load sample image");
        const blob = await res.blob();
        
        const fileName = `demo_${sampleKey}.jpg`;
        currentFile = new File([blob], fileName, { type: "image/jpeg" });

        imagePreview.src = URL.createObjectURL(blob);
        previewBox.classList.remove("hidden");
        document.querySelector(".dropzone-content").classList.add("hidden");
        btnAnalyze.disabled = false;

        // Auto-fill note & plant selector for demonstration
        scanNotes.value = `Demo Test: ${btn.textContent.trim()}`;
        if (sampleKey === "apple_scab") selectPlant("Apple");
        else if (sampleKey === "tomato_early_blight") selectPlant("Tomato");
        else if (sampleKey === "corn_rust") selectPlant("Corn");
        else if (sampleKey === "healthy_pepper") selectPlant("Pepper");

      } catch (err) {
        console.error("Failed to load sample:", err);
      }
    });
  });

  // 4. GRAD-CAM VIEW SWITCHER BUTTONS
  const camViewBtns = document.querySelectorAll(".cam-view-btn");
  camViewBtns.forEach(btn => {
    btn.addEventListener("click", () => {
      camViewBtns.forEach(b => b.classList.remove("active"));
      btn.classList.add("active");
      const view = btn.getAttribute("data-view");
      if (currentGradcamData[view]) {
        gradcamImage.src = currentGradcamData[view];
      }
    });
  });

  // 5. FILE DROP HANDLING
  ["dragenter", "dragover"].forEach(name => {
    dropzoneArea.addEventListener(name, (e) => {
      e.preventDefault();
      dropzoneArea.classList.add("dragover");
    });
  });

  ["dragleave", "drop"].forEach(name => {
    dropzoneArea.addEventListener(name, (e) => {
      e.preventDefault();
      dropzoneArea.classList.remove("dragover");
    });
  });

  dropzoneArea.addEventListener("drop", (e) => {
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelected(e.dataTransfer.files[0]);
    }
  });

  fileInput.addEventListener("change", (e) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelected(e.target.files[0]);
    }
  });

  function handleFileSelected(file) {
    if (!file.type.startsWith("image/")) {
      alert("Please upload a valid image file (JPG, PNG, WebP).");
      return;
    }
    sampleButtons.forEach(b => b.classList.remove("active"));
    currentFile = file;
    const reader = new FileReader();
    reader.onload = (e) => {
      imagePreview.src = e.target.result;
      previewBox.classList.remove("hidden");
      document.querySelector(".dropzone-content").classList.add("hidden");
      btnAnalyze.disabled = false;
    };
    reader.readAsDataURL(file);
  }

  btnRemoveImage.addEventListener("click", (e) => {
    e.stopPropagation();
    currentFile = null;
    fileInput.value = "";
    imagePreview.src = "";
    previewBox.classList.add("hidden");
    document.querySelector(".dropzone-content").classList.remove("hidden");
    btnAnalyze.disabled = true;
    sampleButtons.forEach(b => b.classList.remove("active"));
  });

  // 6. CAMERA HANDLING
  toggleUpload.addEventListener("click", () => {
    stopCamera();
    toggleUpload.classList.add("active");
    toggleCamera.classList.remove("active");
    dropzoneArea.classList.remove("hidden");
    cameraArea.classList.add("hidden");
  });

  toggleCamera.addEventListener("click", async () => {
    toggleCamera.classList.add("active");
    toggleUpload.classList.remove("active");
    dropzoneArea.classList.add("hidden");
    cameraArea.classList.remove("hidden");
    sampleButtons.forEach(b => b.classList.remove("active"));
    startCamera();
  });

  async function startCamera() {
    try {
      cameraStream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "environment", width: { ideal: 640 }, height: { ideal: 480 } }
      });
      webcamVideo.srcObject = cameraStream;
      btnCapture.classList.remove("hidden");
      btnRetake.classList.add("hidden");
    } catch (err) {
      alert("Camera access denied or not available. Please use file upload instead.");
      toggleUpload.click();
    }
  }

  function stopCamera() {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      cameraStream = null;
    }
  }

  btnCapture.addEventListener("click", () => {
    const context = cameraCanvas.getContext("2d");
    cameraCanvas.width = webcamVideo.videoWidth || 640;
    cameraCanvas.height = webcamVideo.videoHeight || 480;
    context.drawImage(webcamVideo, 0, 0, cameraCanvas.width, cameraCanvas.height);

    cameraCanvas.toBlob((blob) => {
      currentFile = new File([blob], `camera_scan_${Date.now()}.jpg`, { type: "image/jpeg" });
      btnAnalyze.disabled = false;
      btnCapture.classList.add("hidden");
      btnRetake.classList.remove("hidden");
    }, "image/jpeg");
  });

  btnRetake.addEventListener("click", () => {
    currentFile = null;
    btnAnalyze.disabled = true;
    btnRetake.classList.add("hidden");
    btnCapture.classList.remove("hidden");
  });

  // 7. RUN INFERENCE & DIAGNOSIS
  btnAnalyze.addEventListener("click", async () => {
    if (!currentFile) return;

    btnAnalyze.disabled = true;
    const btnText = btnAnalyze.querySelector(".btn-text");
    const spinner = btnAnalyze.querySelector(".spinner");
    btnText.textContent = "Analyzing Leaf with Deep Learning...";
    spinner.classList.remove("hidden");

    try {
      const formData = new FormData();
      formData.append("file", currentFile);
      const notes = scanNotes.value.trim();
      const selectedCrop = cropSelector ? cropSelector.value : "auto";

      const params = new URLSearchParams();
      if (notes) params.append("notes", notes);
      if (selectedCrop && selectedCrop !== "auto") params.append("crop_filter", selectedCrop);

      const url = params.toString() ? `/api/predict?${params.toString()}` : "/api/predict";
      const response = await fetch(url, {
        method: "POST",
        body: formData
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Diagnosis failed");
      }

      const data = await response.json();
      renderDiagnosisResult(data);

    } catch (err) {
      alert(`Error during analysis: ${err.message}`);
    } finally {
      btnAnalyze.disabled = false;
      btnText.textContent = "🔬 Run Deep Learning Diagnosis";
      spinner.classList.add("hidden");
    }
  });

  function renderDiagnosisResult(data) {
    resultsPlaceholder.classList.add("hidden");
    resultsContent.classList.remove("hidden");

    // Populate primary badges
    resCropBadge.textContent = data.crop;
    resDiseaseName.textContent = data.disease;

    // Severity styling
    resSeverityBadge.textContent = `${data.severity} Severity`;
    resSeverityBadge.className = "badge-severity";
    const sevKey = data.severity.toLowerCase();
    resSeverityBadge.classList.add(sevKey);

    // Radial confidence gauge
    const confInt = Math.round(data.confidence * 100);
    radialProgress.setAttribute("stroke-dasharray", `${confInt}, 100`);
    resConfidenceText.textContent = `${confInt}%`;

    // Store Grad-CAM views
    currentGradcamData = data.gradcam;
    // Set to overlay by default
    camViewBtns.forEach(b => b.classList.remove("active"));
    const overlayBtn = document.querySelector('.cam-view-btn[data-view="overlay"]');
    if (overlayBtn) overlayBtn.classList.add("active");
    gradcamImage.src = currentGradcamData.overlay || currentGradcamData.original;

    // Render Top 5 Predictions
    topPredictionsList.innerHTML = "";
    data.top_predictions.forEach(pred => {
      const row = document.createElement("div");
      row.className = "pred-row";
      const pctValue = Math.round(pred.probability * 100);
      row.innerHTML = `
        <div class="pred-meta">
          <span class="pred-name">${pred.crop} – ${pred.disease}</span>
          <span class="pred-pct">${pctValue}%</span>
        </div>
        <div class="bar-track">
          <div class="bar-fill" style="width: ${pctValue}%"></div>
        </div>
      `;
      topPredictionsList.appendChild(row);
    });

    // Agricultural Guidance
    resSymptoms.textContent = data.symptoms;
    resOrganic.textContent = data.organic_treatment;
    resChemical.textContent = data.chemical_treatment;
    resPrevention.textContent = data.prevention;

    // Plant Context Switcher Buttons
    const pillCrops = document.querySelectorAll(".pill-crop");
    const activeFilter = data.applied_filter ? data.applied_filter.toLowerCase() : "auto";
    pillCrops.forEach(pill => {
      const pillCropVal = pill.getAttribute("data-crop");
      if (pillCropVal.toLowerCase() === activeFilter || (activeFilter === "auto" && pillCropVal === "auto")) {
        pill.classList.add("active");
      } else {
        pill.classList.remove("active");
      }

      pill.onclick = () => {
        selectPlant(pillCropVal);
      };
    });

    // Smooth scroll to results
    resultsContent.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }

  // 8. PRINT REPORT
  if (btnPrintReport) {
    btnPrintReport.addEventListener("click", () => {
      window.print();
    });
  }

  // 9. ENCYCLOPEDIA TAB
  async function loadEncyclopedia() {
    const grid = document.getElementById("encyclopedia-grid");
    if (Object.keys(allDiseases).length === 0) {
      grid.innerHTML = '<p class="subtext">Loading plant disease encyclopedia...</p>';
      try {
        const res = await fetch("/api/diseases");
        const json = await res.json();
        allDiseases = json.diseases;
      } catch (e) {
        grid.innerHTML = '<p class="subtext">Failed to load disease library.</p>';
        return;
      }
    }
    renderEncyclopediaCards();
  }

  function renderEncyclopediaCards(searchTerm = "", cropFilter = "all") {
    const grid = document.getElementById("encyclopedia-grid");
    grid.innerHTML = "";

    const entries = Object.entries(allDiseases).filter(([key, val]) => {
      const matchesSearch = val.crop.toLowerCase().includes(searchTerm.toLowerCase()) || 
                            val.disease.toLowerCase().includes(searchTerm.toLowerCase()) ||
                            val.symptoms.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCrop = (cropFilter === "all") || val.crop.toLowerCase().includes(cropFilter.toLowerCase());
      return matchesSearch && matchesCrop;
    });

    if (entries.length === 0) {
      grid.innerHTML = '<p class="subtext">No matching plant diseases found.</p>';
      return;
    }

    entries.forEach(([key, d]) => {
      const card = document.createElement("div");
      card.className = "disease-card";
      const sevClass = d.severity.toLowerCase();
      card.innerHTML = `
        <div>
          <span class="badge-crop">${d.crop}</span>
          <span class="badge-severity ${sevClass}">${d.severity}</span>
          <h3>${d.disease}</h3>
          <p class="card-symptoms"><strong>Symptoms:</strong> ${d.symptoms}</p>
        </div>
        <div class="card-footer">
          <p><strong>Remedy:</strong> ${d.organic_treatment}</p>
        </div>
      `;
      grid.appendChild(card);
    });
  }

  const diseaseSearch = document.getElementById("disease-search");
  if (diseaseSearch) {
    diseaseSearch.addEventListener("input", (e) => {
      const activeChip = document.querySelector(".chip.active");
      const crop = activeChip ? activeChip.getAttribute("data-crop") : "all";
      renderEncyclopediaCards(e.target.value, crop);
    });
  }

  const cropChips = document.querySelectorAll(".filter-chips .chip");
  cropChips.forEach(chip => {
    chip.addEventListener("click", () => {
      cropChips.forEach(c => c.classList.remove("active"));
      chip.classList.add("active");
      const crop = chip.getAttribute("data-crop");
      renderEncyclopediaCards(diseaseSearch ? diseaseSearch.value : "", crop);
    });
  });

  // 10. HISTORY TAB
  async function loadHistoryAndStats() {
    try {
      const [histRes, statsRes] = await Promise.all([
        fetch("/api/history?limit=30"),
        fetch("/api/stats")
      ]);

      const histData = await histRes.json();
      const statsData = await statsRes.json();

      document.getElementById("stat-total-scans").textContent = statsData.total_scans || 0;
      document.getElementById("stat-top-crop").textContent = 
        statsData.top_crops && statsData.top_crops.length > 0 ? statsData.top_crops[0].crop : "—";
      document.getElementById("stat-top-disease").textContent = 
        statsData.top_diseases && statsData.top_diseases.length > 0 ? statsData.top_diseases[0].disease : "—";

      const tbody = document.getElementById("history-table-body");
      tbody.innerHTML = "";

      if (!histData.scans || histData.scans.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" style="text-align: center; color: var(--text-muted); padding: 2.5rem;">No previous scans recorded yet.</td></tr>';
        return;
      }

      histData.scans.forEach(scan => {
        const tr = document.createElement("tr");
        const sevClass = (scan.severity || "medium").toLowerCase();
        const confPct = Math.round(scan.confidence * 100);
        tr.innerHTML = `
          <td>#${scan.id}</td>
          <td>${scan.timestamp}</td>
          <td><strong>${scan.crop}</strong></td>
          <td>${scan.disease}</td>
          <td><span class="pred-pct">${confPct}%</span></td>
          <td><span class="badge-severity ${sevClass}">${scan.severity}</span></td>
          <td style="color: var(--text-muted);">${scan.notes || "—"}</td>
        `;
        tbody.appendChild(tr);
      });

    } catch (e) {
      console.error("Error loading scan history:", e);
    }
  }

  const btnClearHistory = document.getElementById("btn-clear-history");
  if (btnClearHistory) {
    btnClearHistory.addEventListener("click", async () => {
      if (confirm("Are you sure you want to clear all scan history records?")) {
        await fetch("/api/history", { method: "DELETE" });
        loadHistoryAndStats();
      }
    });
  }

});
