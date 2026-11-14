# EXP-09: File Uploads and Download Verification

**Experiment ID:** EXP-09  
**Category:** File System & Download Completion  
**Status:** Verified & Passing (2/2 Tests Passed)  
**Author:** Principal SDET / Reliability Engineering Specialist  

---

## 1. Hypothesis
Direct dispatch of absolute file paths to `<input type="file">` elements avoids flaky OS-level file dialogs. For downloads, verifying the existence of a download button is insufficient; true reliability requires polling the isolated download directory, filtering out transient in-progress download extensions (`.crdownload`, `.tmp`), and validating SHA256 checksums.

---

## 2. Experimental Setup
- **Target Applications:**
  - The Internet (`/upload`)
  - Controlled Local App (`/scenarios/download-file?filename=...`)
- **Scenarios Investigated:**
  1. File Upload: Generating a specimen in `tmp_path`, sending path via `FileManager.upload_file`, submitting, and asserting server confirmation.
  2. File Download: Downloading file into `isolated_download_dir`, waiting for completion, asserting file size > 0, and validating cryptographic SHA256 checksum.

---

## 3. Empirical Observations & Results

| Test Scenario | Action | Outcome | Verified Evidence |
|---|---|---|---|
| `test_exp09_file_upload_verification` | Upload `brel_upload_test.txt` | **PASSED** | Verified: "File Uploaded!", filename matched |
| `test_exp09_file_download_and_integrity_check` | Download & SHA256 audit | **PASSED** | Verified: SHA256 checksum matched expected hash |

---

## 4. Engineering Conclusion
1. **Parallel Worker Isolation (ADR-006):** In parallel test runs, using a shared global download directory causes race conditions and file collisions. Function-scoped, UUID-tagged temporary directories eliminate download collisions entirely.
2. **Download Polling:** Polling must discard `.crdownload` temporary files to prevent reading incomplete byte streams.
