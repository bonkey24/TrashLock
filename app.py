"""
app.py – Streamlit entry point for TrashLock.

A software-only biometric security prototype: TrashLock.
"Your body as a password"

Run with:
    streamlit run app.py

Architecture:
- Restyled to match the Stitch design system (dark theme, Space Grotesk typography, cards, badges).
- Modular sidebar navigation powered by a PAGES dictionary:
  Enrol, Login, Analysis, Test Log, About.
- Strict privacy: only 512-dimensional numeric embeddings are stored in SQLite;
  captured photos are NEVER saved to disk or persistent storage.
- Analysis page: evaluates biometric performance (FAR, FRR, EER) on LFW public benchmark.
- Test Log page: tracks physical and experimental presentation attack scenarios.
- About page: student-friendly breakdown of biometrics, error rates, and vulnerabilities.
"""

import os
import io
from collections import defaultdict
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_lfw_people

from db import (
    init_db,
    save_user,
    load_users,
    delete_user,
    delete_all_users,
    user_exists,
    verify_pin,
    save_test_log,
    load_test_logs,
    clear_test_logs,
)
from face_utils import get_embedding, cosine_distance, average_templates
from ui import (
    inject_css,
    page_header,
    card,
    success_badge,
    error_badge,
    metric_card,
    result_metrics_panel,
    privacy_note,
    render_test_log_table,
    style_figure,
)

# ---------------------------------------------------------------------------
# App configuration (must be called first)
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="TrashLock",
    page_icon="🔐",
    layout="wide"
)

# Inject custom Stitch CSS and Google Fonts
inject_css()

# Ensure the SQLite database tables exist on startup
init_db()


# ===========================================================================
# PAGE 1: Enrol
# ===========================================================================
def page_enrol():
    st.header("Enrol")
    st.caption("Your body as a password")
    st.markdown(
        "<p style='color: #9D8D8F; font-size: 14px; margin-top: -6px; margin-bottom: 24px; font-family: \"Space Grotesk\", sans-serif;'>"
        "Register a new participant by capturing face photos and generating a 512-D face embedding."
        "</p>",
        unsafe_allow_html=True
    )

    col_form, col_cam = st.columns([5, 7], gap="large")

    with col_form:
        with st.container(border=True):
            card("Participant details", "Assign a display name and optional fallback PIN.")
            name = st.text_input("Name", placeholder="Enter full name", key="enrol_name")
            pin = st.text_input("PIN", type="password", placeholder="4-digit PIN", key="enrol_pin")
            st.caption("Used when Require PIN is active during login")

            if "enrol_embeddings" not in st.session_state:
                st.session_state.enrol_embeddings = []

            total_max = 5
            min_required = 3
            taken = len(st.session_state.enrol_embeddings)

            if taken >= min_required:
                if st.button("💾 Save enrolment", type="primary", use_container_width=True):
                    clean_name = name.strip()
                    clean_pin = pin.strip()

                    # Robustness: Empty name check
                    if not clean_name:
                        st.error("⚠️ Please enter a name before saving.")
                        return

                    # Robustness: Empty PIN check
                    if not clean_pin:
                        st.error("⚠️ Please enter a PIN before saving.")
                        return

                    # Robustness: Duplicate name check
                    try:
                        if user_exists(clean_name):
                            st.error(
                                f"⚠️ A participant named **'{clean_name}'** is already enrolled. "
                                "Please choose a distinct name or delete the previous enrolment below."
                            )
                            return
                    except Exception as e:
                        st.error(f"Database error during name verification: {e}")
                        return

                    with st.spinner("Averaging templates and storing in database..."):
                        try:
                            template = average_templates(st.session_state.enrol_embeddings)
                            save_user(clean_name, clean_pin, template)
                            st.success(f"🎉 **{clean_name}** enrolled successfully!")
                            st.session_state.enrol_embeddings = []
                            st.rerun()
                        except Exception as e:
                            st.error(f"Database error while saving user: {e}")

            privacy_note()

        # Enrolled participants list with individual delete buttons
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            try:
                enrolled_users = load_users()
            except Exception as e:
                enrolled_users = []
                st.error(f"Error loading enrolled users: {e}")

            card("Enrolled participants", f"{len(enrolled_users)} identity/identities currently enrolled")

            if not enrolled_users:
                st.info("No participants enrolled yet. Capture photos on the right to enrol.")
            else:
                for u in enrolled_users:
                    u_col1, u_col2 = st.columns([4, 1])
                    with u_col1:
                        st.markdown(
                            f"<div style='padding-top: 6px; font-family: \"Space Grotesk\", sans-serif;'>"
                            f"👤 <strong>{u['name']}</strong> "
                            f"<span style='color: #9D8D8F; font-size: 12px;'>(ID: {u['id']})</span>"
                            f"</div>",
                            unsafe_allow_html=True
                        )
                    with u_col2:
                        if st.button("Delete", key=f"del_user_{u['id']}", type="secondary", use_container_width=True):
                            try:
                                delete_user(u["id"])
                                st.success(f"Deleted {u['name']}.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error deleting user: {e}")

                st.divider()
                if st.button("🗑️ Delete all users", type="secondary", use_container_width=True):
                    try:
                        delete_all_users()
                        st.session_state.enrol_embeddings = []
                        st.warning("All enrolled users have been deleted from the database.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error resetting database: {e}")

    with col_cam:
        with st.container(border=True):
            if "enrol_embeddings" not in st.session_state:
                st.session_state.enrol_embeddings = []

            taken = len(st.session_state.enrol_embeddings)

            col_hdr1, col_hdr2 = st.columns([3, 2])
            with col_hdr1:
                card("Webcam preview")
            with col_hdr2:
                st.markdown(
                    f"""
                    <div style="text-align: right; margin-top: 4px;">
                        <span style="background-color: #FAED26; color: #46344E; font-family: 'JetBrains Mono', monospace; font-size: 13px; font-weight: 700; padding: 4px 12px; border-radius: 9999px;">
                            {taken} / 5 photos
                        </span>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.progress(taken / 5)

            if taken < 5:
                photo = st.camera_input(f"Capture photo {taken + 1} of 5", key=f"enrol_cam_{taken}")
                if photo is not None:
                    try:
                        with st.spinner("Detecting face and computing embedding..."):
                            emb = get_embedding(photo.getvalue())
                            st.session_state.enrol_embeddings.append(emb)
                        st.success(f"✅ Photo {taken + 1} accepted – face detected!")
                        st.rerun()
                    except ValueError as err:
                        st.error(f"⚠️ {err}")
            else:
                st.info("You have captured the maximum of 5 photos. Click **Save enrolment** on the left.")

            if taken > 0:
                if st.button("🔄 Clear Captured Photos", type="secondary"):
                    st.session_state.enrol_embeddings = []
                    st.rerun()


# ===========================================================================
# PAGE 2: Login
# ===========================================================================
def page_login():
    col_head1, col_head2 = st.columns([4, 1])
    with col_head1:
        st.header("Login")
        st.caption("Your body as a password")
        st.markdown(
            "<p style='color: #9D8D8F; font-size: 14px; margin-top: -6px; margin-bottom: 24px; font-family: \"Space Grotesk\", sans-serif;'>"
            "Compare live webcam embeddings against enrolled templates using cosine distance."
            "</p>",
            unsafe_allow_html=True
        )
    with col_head2:
        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        require_pin = st.toggle("Require PIN", value=False, help="Enable two-factor authentication.")

    try:
        users = load_users()
    except Exception as e:
        users = []
        st.error(f"Database error loading users: {e}")

    # Robustness: No users enrolled check
    if not users:
        st.warning("⚠️ No participants enrolled yet. Please navigate to the **Enrol** page first to register your face.")
        return

    col_cam, col_res = st.columns([7, 5], gap="large")

    with col_cam:
        with st.container(border=True):
            card("Webcam feed", "Align face in camera and capture frame")
            photo = st.camera_input("Take a photo to authenticate", key="login_camera")

    with col_res:
        with st.container(border=True):
            card("Verification result", f"Nearest template in gallery ({len(users)} enrolled)")

            if photo is None:
                st.info("📷 Please capture a photo in the webcam feed to authenticate.")
                st.session_state.pop("last_login_match", None)
            else:
                try:
                    with st.spinner("Extracting facial features..."):
                        login_emb = get_embedding(photo.getvalue())
                except ValueError as err:
                    st.error(f"⚠️ {err}")
                    return
                except Exception as err:
                    st.error(f"Unexpected error processing photo: {err}")
                    return

                best_distance = float("inf")
                best_user = None

                for user in users:
                    dist = cosine_distance(login_emb, user["embedding"])
                    if dist < best_distance:
                        best_distance = dist
                        best_user = user

                similarity_score = max(0.0, 1.0 - best_distance)
                threshold = st.session_state.match_threshold
                is_match = best_distance < threshold
                decision_str = f"{best_distance:.3f} {'≤' if is_match else '>'} {threshold:.3f}"

                if is_match:
                    success_badge(f"Access granted: {best_user['name']}", "Distance within match threshold")
                else:
                    error_badge("Access denied", "Distance exceeds match threshold")

                result_metrics_panel(best_user["name"], best_distance, similarity_score, decision_str)

                if is_match:
                    if require_pin:
                        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
                        st.info(f"👤 Face matched **{best_user['name']}**. Please enter your PIN:")
                        entered_pin = st.text_input("Enter PIN", type="password", key="login_pin_input")
                        if entered_pin:
                            if verify_pin(entered_pin, best_user["pin_hash"], best_user["pin_salt"]):
                                st.success(f"✅ Access granted: {best_user['name']}")
                                st.balloons()
                            else:
                                st.error("❌ Access denied: Incorrect PIN.")
                    else:
                        st.balloons()


# ===========================================================================
# PAGE 3: Analysis (Biometric Performance Evaluation)
# ===========================================================================
@st.cache_data(show_spinner=False)
def _load_lfw_dataset():
    """Load LFW dataset with min_faces_per_person=10 from the project workspace."""
    data_home = os.path.join(os.path.dirname(os.path.abspath(__file__)), "lfw_data")
    return fetch_lfw_people(data_home=data_home, min_faces_per_person=10, color=True)


@st.cache_data(show_spinner=False)
def _extract_lfw_embedding_cached(img_bytes: bytes) -> np.ndarray:
    """Cache individual image embeddings so re-loading or re-evaluating is instant."""
    return get_embedding(img_bytes)


def page_analysis():
    st.header("Analysis")
    st.caption("Your body as a password")
    st.markdown(
        "<p style='color: #9D8D8F; font-size: 14px; margin-top: -6px; margin-bottom: 24px; font-family: \"Space Grotesk\", sans-serif;'>"
        "Evaluation of False Accept Rate (FAR), False Reject Rate (FRR), and Equal Error Rate (EER) across the enrolled dataset."
        "</p>",
        unsafe_allow_html=True
    )

    # State container for loaded LFW embeddings
    if "lfw_embeddings" not in st.session_state:
        st.session_state.lfw_embeddings = None

    # Load button
    col_btn, _ = st.columns([1, 3])
    with col_btn:
        load_clicked = st.button("📥 Load LFW sample", type="primary", use_container_width=True)

    if load_clicked:
        with st.spinner("Loading LFW face images from disk..."):
            try:
                lfw = _load_lfw_dataset()
            except Exception as e:
                st.error(f"Error loading LFW dataset: {e}")
                return

        people_indices = defaultdict(list)
        for idx, target_id in enumerate(lfw.target):
            people_indices[target_id].append(idx)

        # Select ~14 people with at least 5 images each for fast, reliable evaluation (~70 images)
        max_people = 14
        max_images_per_person = 5
        selected = []
        for target_id, indices in people_indices.items():
            if len(indices) >= max_images_per_person:
                selected.append((target_id, indices[:max_images_per_person]))
                if len(selected) >= max_people:
                    break

        tasks = []
        for target_id, indices in selected:
            person_name = lfw.target_names[target_id]
            for idx in indices:
                tasks.append((person_name, lfw.images[idx]))

        progress_bar = st.progress(0, text="Computing Facenet embeddings with facenet-pytorch...")
        person_embeddings = defaultdict(list)
        skipped_faces = 0

        import cv2
        for i, (name, img) in enumerate(tasks):
            progress_bar.progress((i + 1) / len(tasks), text=f"Processing {name} ({i+1}/{len(tasks)})...")
            arr = (img * 255).astype(np.uint8) if img.max() <= 1.0 else img.astype(np.uint8)
            bgr = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
            _, buf = cv2.imencode(".jpg", bgr)

            try:
                emb = _extract_lfw_embedding_cached(buf.tobytes())
                person_embeddings[name].append(emb)
            except ValueError:
                skipped_faces += 1
                continue

        progress_bar.empty()

        valid_embeddings = {k: v for k, v in person_embeddings.items() if len(v) >= 2}
        st.session_state.lfw_embeddings = valid_embeddings
        st.success(f"✅ Processed {len(tasks)} images ({skipped_faces} skipped) across {len(valid_embeddings)} people!")
        st.rerun()

    # Robustness: Opening Analysis before loading data
    if st.session_state.lfw_embeddings is None:
        st.info("👆 Click **Load LFW sample** above to load face images, extract embeddings, and generate biometric curves.")
        st.caption(
            "ℹ️ **Public Dataset Note:** Labeled Faces in the Wild (LFW) is a public benchmark dataset. "
            "Measured error rates (FAR, FRR, EER) depend on sample size, crop alignment, lighting, pose, "
            "and demographic distributions in the dataset."
        )
        return

    embeddings_dict = st.session_state.lfw_embeddings

    # --- Build genuine and impostor pairs ---
    from itertools import combinations
    genuine_distances = []
    impostor_distances = []

    for person_name, embs in embeddings_dict.items():
        for e1, e2 in combinations(embs, 2):
            genuine_distances.append(cosine_distance(e1, e2))

    person_names = list(embeddings_dict.keys())
    for i in range(len(person_names)):
        for j in range(i + 1, len(person_names)):
            for e1 in embeddings_dict[person_names[i]]:
                for e2 in embeddings_dict[person_names[j]]:
                    impostor_distances.append(cosine_distance(e1, e2))

    gen_arr = np.array(genuine_distances)
    imp_arr = np.array(impostor_distances)

    # Top 3 Dataset Summary Metric Cards matching analysis.html
    m1, m2, m3 = st.columns(3)
    with m1:
        metric_card("People", len(embeddings_dict), "LFW images per person")
    with m2:
        metric_card("Genuine pairs", len(gen_arr), "Same-identity comparisons")
    with m3:
        metric_card("Impostor pairs", len(imp_arr), "Cross-identity comparisons")

    # --- FAR, FRR, and EER calculations ---
    threshold_range = np.linspace(0.10, 0.80, 71)
    far_curve = []
    frr_curve = []

    for t in threshold_range:
        far = np.mean(imp_arr < t)
        frr = np.mean(gen_arr >= t)
        far_curve.append(far)
        frr_curve.append(frr)

    far_curve = np.array(far_curve)
    frr_curve = np.array(frr_curve)

    diffs = np.abs(far_curve - frr_curve)
    eer_idx = np.argmin(diffs)
    eer_threshold = threshold_range[eer_idx]
    eer_value = (far_curve[eer_idx] + frr_curve[eer_idx]) / 2.0

    current_threshold = st.session_state.match_threshold
    current_far = float(np.mean(imp_arr < current_threshold))
    current_frr = float(np.mean(gen_arr >= current_threshold))

    # --- Charts Row matching analysis.html ---
    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    ch_col1, ch_col2 = st.columns(2, gap="large")

    with ch_col1:
        with st.container(border=True):
            card("FAR vs FRR", "Error rate across cosine distance thresholds")
            fig1, ax1 = plt.subplots(figsize=(8, 4.5))
            style_figure(fig1, ax1)

            # FRR curve: #FAED26 (yellow), FAR curve: #F4C7B8 (light peach, high contrast)
            ax1.plot(threshold_range, frr_curve * 100, label="FRR (False Reject)", color="#FAED26", linewidth=2.5)
            ax1.plot(threshold_range, far_curve * 100, label="FAR (False Accept)", color="#F4C7B8", linewidth=2.5)

            # EER intersection marker: edge #FAED26, face #46344E
            ax1.scatter(
                [eer_threshold], [eer_value * 100],
                color="#46344E", s=120, zorder=6, edgecolors="#FAED26", linewidth=2.5,
                label=f"EER ≈ {eer_value * 100:.1f}% @ {eer_threshold:.2f}"
            )

            # Active threshold vertical line: white, dashed, linewidth 2.0
            ax1.axvline(
                current_threshold, color="#FFFFFF", linestyle="--", linewidth=2.0, alpha=0.95,
                label=f"Threshold ({current_threshold:.2f})"
            )

            ax1.set_xlabel("Cosine Distance Threshold", fontsize=12, color="#F5F1E8", labelpad=8)
            ax1.set_ylabel("Error Rate (%)", fontsize=12, color="#F5F1E8", labelpad=8)
            ax1.set_xlim(0.10, 0.80)
            ax1.set_ylim(-2, 102)
            ax1.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, -0.22),
                ncol=2,
                frameon=True,
                facecolor="#46344E",
                edgecolor="#9D8D8F",
                labelcolor="#F5F1E8",
                fontsize=10
            )
            plt.tight_layout()
            st.pyplot(fig1, use_container_width=True)
            plt.close(fig1)

    with ch_col2:
        with st.container(border=True):
            card("Distance distribution", "Genuine vs impostor cosine distance histogram")
            fig2, ax2 = plt.subplots(figsize=(8, 4.5))
            style_figure(fig2, ax2)

            # Genuine histogram: #FAED26, Impostor histogram: #9B786F
            ax2.hist(gen_arr, bins=25, alpha=0.85, label=f"Genuine (Same, n={len(gen_arr)})", color="#FAED26", density=True, rwidth=0.85)
            ax2.hist(imp_arr, bins=25, alpha=0.85, label=f"Impostor (Diff, n={len(imp_arr)})", color="#9B786F", density=True, rwidth=0.85)

            # Active threshold vertical line: white, dashed, linewidth 2.0
            ax2.axvline(
                current_threshold, color="#FFFFFF", linestyle="--", linewidth=2.0, alpha=0.95,
                label=f"Threshold ({current_threshold:.2f})"
            )

            ax2.set_xlabel("Cosine Distance", fontsize=12, color="#F5F1E8", labelpad=8)
            ax2.set_ylabel("Probability Density", fontsize=12, color="#F5F1E8", labelpad=8)
            ax2.set_xlim(0.0, 1.2)
            ax2.legend(
                loc="upper center",
                bbox_to_anchor=(0.5, -0.22),
                ncol=2,
                frameon=True,
                facecolor="#46344E",
                edgecolor="#9D8D8F",
                labelcolor="#F5F1E8",
                fontsize=10
            )
            plt.tight_layout()
            st.pyplot(fig2, use_container_width=True)
            plt.close(fig2)

    # --- Results Table matching analysis.html ---
    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        card("Results table", "Performance at active threshold vs. EER")
        table_data = {
            "Metric": [
                "Active Match Threshold",
                "False Accept Rate (FAR)",
                "False Reject Rate (FRR)",
                "Equal Error Rate (EER)",
                "EER Optimal Threshold"
            ],
            "Value": [
                f"{current_threshold:.2f}",
                f"{current_far:.2%}",
                f"{current_frr:.2%}",
                f"{eer_value:.2%}",
                f"{eer_threshold:.2f}"
            ],
            "Description": [
                "Current distance cutoff chosen via sidebar slider",
                "Impostor pairs incorrectly accepted below this threshold",
                "Genuine user pairs incorrectly rejected at or above this threshold",
                "Theoretical operating point where FAR and FRR are equal",
                "Threshold where the FAR and FRR curves intersect"
            ]
        }
        st.table(pd.DataFrame(table_data))

    st.caption(
        "ℹ️ **Public Dataset Note:** Labeled Faces in the Wild (LFW) is a public benchmark dataset. "
        "Measured error rates (FAR, FRR, EER) depend on sample size, crop alignment, lighting, pose, "
        "and demographic distributions in the dataset."
    )


# ===========================================================================
# PAGE 4: Test Log (Matches temp/test_log.html)
# ===========================================================================
def page_test_log():
    # Header with Download CSV action button
    col_h1, col_h2 = st.columns([4, 1])
    with col_h1:
        st.header("Test Log")
        st.caption("Your body as a password")
        st.markdown(
            "<p style='color: #9D8D8F; font-size: 14px; margin-top: -6px; margin-bottom: 24px; font-family: \"Space Grotesk\", sans-serif;'>"
            "Record verification scenarios, compare expected vs actual outcomes, and export results."
            "</p>",
            unsafe_allow_html=True
        )

    # Load test logs from SQLite (starts empty, no seeding)
    logs = load_test_logs()

    # Download CSV button
    with col_h2:
        st.markdown("<div style='margin-top: 14px;'></div>", unsafe_allow_html=True)
        if logs:
            df_export = pd.DataFrame(logs)[["test_case", "expected", "actual", "status", "created_at"]]
            df_export.columns = ["Test Case", "Expected", "Actual", "Status", "Date"]
            csv_data = df_export.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="📥 Download CSV",
                data=csv_data,
                file_name="trashlock_test_log.csv",
                mime="text/csv",
                use_container_width=True
            )

    # Add row card form
    with st.container(border=True):
        card("Add row", "Record experimental presentation attack or edge-case test result")

        SUGGESTIONS = [
            "Own face (normal lighting)",
            "Classmate (different person)",
            "Phone photo (screen replay)",
            "Printed photo (paper spoof)",
            "Dim light / poor lighting",
            "Glasses / accessory change",
            "Wrong PIN (two-factor test)",
            "Custom scenario...",
        ]

        f_col1, f_col2, f_col3, f_col4 = st.columns([4, 3, 3, 2])

        with f_col1:
            chosen_case = st.selectbox("Test case scenario", SUGGESTIONS)
            if chosen_case == "Custom scenario...":
                final_test_case = st.text_input("Enter scenario description", placeholder="e.g. Side profile 45°")
            else:
                final_test_case = chosen_case

        with f_col2:
            expected_val = st.selectbox("Expected result", ["Access granted", "Access denied"])

        with f_col3:
            actual_val = st.text_input(
                "Actual result",
                value="",
                placeholder="e.g. Access granted",
                key="test_log_actual_input"
            )

        with f_col4:
            st.markdown("<div style='margin-top: 26px;'></div>", unsafe_allow_html=True)
            status_choice = st.selectbox("Status", ["Pass", "Fail"], index=0)

        btn_col, clear_col = st.columns([2, 8])
        with btn_col:
            if st.button("➕ Add row", type="primary", use_container_width=True):
                clean_test_case = final_test_case.strip() if final_test_case else ""
                clean_actual = actual_val.strip() if actual_val else ""

                if not clean_test_case:
                    st.error("⚠️ Please enter a test case scenario.")
                elif not clean_actual:
                    st.error("⚠️ Please enter the actual result before saving.")
                else:
                    save_test_log(clean_test_case, expected_val, clean_actual, status_choice)
                    st.success("Test case added successfully!")
                    st.rerun()

    # Table displaying rows with coloured badges
    st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
    with st.container(border=True):
        card("Recorded test cases", f"{len(logs)} test scenario(s) logged")
        render_test_log_table(logs)

        # Clear logs action
        if logs:
            st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
            if st.button("🗑️ Clear Test Log", type="secondary"):
                clear_test_logs()
                st.warning("All test log entries cleared.")
                st.rerun()


# ===========================================================================
# PAGE 5: About (Student-Friendly Educational Guide)
# ===========================================================================
def page_about():
    st.header("About")
    st.caption("Your body as a password")
    st.markdown(
        "<p style='color: #9D8D8F; font-size: 14px; margin-top: -6px; margin-bottom: 24px; font-family: \"Space Grotesk\", sans-serif;'>"
        "Understanding biometric security, error trade-offs, and presentation attack vulnerabilities."
        "</p>",
        unsafe_allow_html=True
    )

    col1, col2 = st.columns(2, gap="large")

    with col1:
        with st.container(border=True):
            card("Core Biometric Concepts", "How face recognition authenticates users")
            st.markdown(
                r"""
                - **Enrolment**: Capturing 3–5 face photos to build a stable biometric representation across slight variations in expression and lighting.
                - **Biometric Template**: A compact **512-dimensional numeric vector** extracted by the neural network (`InceptionResnetV1`). Photos are **never** stored on disk.
                - **Matching & Distance**: Comparing vectors using **cosine distance** ($d \in [0, 2]$):
                  - $0.0$: Identical direction / same face.
                  - $1.0$: Orthogonal / unrelated vectors.
                  - $2.0$: Completely opposite direction.
                - **Decision Threshold ($\theta$)**: The cut-off line. If $\text{distance} < \theta$, access is **granted**; otherwise, access is **denied**.
                - **FAR (False Accept Rate)**: Share of impostors incorrectly accepted ($d < \theta$). A critical **security** flaw.
                - **FRR (False Reject Rate)**: Share of genuine users incorrectly rejected ($d \ge \theta$). A frustrating **usability** issue.
                - **EER (Equal Error Rate)**: The threshold where $\text{FAR} = \text{FRR}$. Lower EER indicates a higher-quality biometric sensor.
                """
            )

        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            card("Privacy & Data Guarantee", "Local processing with zero image retention")
            st.markdown(
                """
                TrashLock enforces strict privacy guarantees:
                - **No persistent photos**: Webcam frames and LFW sample images are processed in-memory and immediately discarded after embedding inference.
                - **Mathematical vectors only**: SQLite stores only 512 numbers per enrolled participant.
                - **Irreversibility**: A 512-d embedding cannot be reverse-engineered back into the original face photo.
                - **Cryptographic PIN Storage**: Fallback PINs are salted with 32 random hex characters and hashed with SHA-256 before storage.
                """
            )

    with col2:
        with st.container(border=True):
            card("Biometric Risks & Vulnerabilities", "Why your body cannot replace all passwords")
            st.markdown(
                """
                While biometrics offer effortless convenience, they present unique structural security risks:

                1. **Permanence (Cannot be reset)**:
                   - If a password is leaked, you change it in seconds.
                   - If your biometric template is stolen or spoofed, you **cannot** change your face.

                2. **Presentation Attacks (Spoofing)**:
                   - Simple cameras without hardware depth sensors (RGB-only webcams) are susceptible to presentation attacks:
                     - **2D printouts**: High-resolution photos printed on paper.
                     - **Screen replays**: Displaying photos or videos on a smartphone or tablet screen.
                     - **Deepfakes**: AI-generated face syntheses mimicking genuine facial movements.

                3. **Demographic Bias & Lighting**:
                   - Neural networks can exhibit divergent accuracy across skin tones, genders, ages, and non-ideal lighting conditions.

                4. **Privacy & Passive Consent**:
                   - Unlike entering a PIN or password which requires conscious intent, your face is public and can be captured from a distance without explicit awareness.

                5. **The Need for Two-Factor Authentication (2FA)**:
                   - Combining **what you are** (biometrics) with **what you know** (PIN/password) ensures that presentation attacks alone cannot breach sensitive systems.
                """
            )


# ===========================================================================
# NAVIGATION (Modular design – easy to add About, etc.)
# ===========================================================================
PAGES = {
    "Enrol": page_enrol,
    "Login": page_login,
    "Analysis": page_analysis,
    "Test Log": page_test_log,
    "About": page_about,
}

# Sidebar brand header matching Stitch sidebar
st.sidebar.markdown(
    """
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 24px;">
        <div style="width: 40px; height: 40px; border-radius: 8px; background-color: #FAED26; color: #46344E; display: flex; align-items: center; justify-content: center; font-size: 20px; font-weight: bold; flex-shrink: 0;">
            👤
        </div>
        <div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 20px; font-weight: 700; color: #FAED26; line-height: 1.1;">TrashLock</div>
            <div style="font-family: 'Space Grotesk', sans-serif; font-size: 12px; color: #F5F1E8; opacity: 0.85;">Your body as a password</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

selected_page = st.sidebar.radio(
    "Navigate",
    list(PAGES.keys()),
    format_func=lambda x: {
        "Enrol": "👤 Enrol",
        "Login": "🛡️ Login",
        "Analysis": "📊 Analysis",
        "Test Log": "📋 Test Log",
        "About": "ℹ️ About"
    }.get(x, x),
    label_visibility="collapsed"
)

# Sidebar match threshold slider matching Stitch design (default 0.50)
if "match_threshold" not in st.session_state:
    st.session_state.match_threshold = 0.50

st.sidebar.markdown(
    f"""
    <div style="padding-top: 20px; border-top: 1px solid #9D8D8F; margin-top: 28px;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 4px;">
            <span style="font-family: 'Space Grotesk', sans-serif; font-size: 13px; font-weight: 600; color: #F5F1E8;">Match threshold</span>
            <span style="font-family: 'JetBrains Mono', monospace; font-size: 14px; font-weight: 700; color: #FAED26;">{st.session_state.match_threshold:.2f}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.session_state.match_threshold = st.sidebar.slider(
    "Match threshold",
    min_value=0.10,
    max_value=0.80,
    value=st.session_state.match_threshold,
    step=0.01,
    help="Cosine distance cut-off. Lower values are stricter; higher values are more lenient.",
    label_visibility="collapsed"
)

st.sidebar.markdown(
    """
    <div style="display: flex; justify-content: space-between; font-size: 11px; color: #9D8D8F; font-family: 'Space Grotesk', sans-serif; margin-top: -8px;">
        <span>0.10 Strict</span>
        <span>0.80 Lenient</span>
    </div>
    """,
    unsafe_allow_html=True
)

# Execute the selected page handler
PAGES[selected_page]()
