from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import re  # 正規表現モジュール
from urllib.parse import urljoin  # 絶対URL生成のため
import os  # ファイル操作のため

import getpass
import traceback

# Web Driverの設定
driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

# ターゲットURLとベースドメイン
target_url = "https://els.sa.dendai.ac.jp/webclass/login.php"
base_domain = "https://els.sa.dendai.ac.jp"

# print(f"Navigating to: {target_url}") # この行はコメントアウト

# WebDriverWaitのタイムアウト時間
wait_timeout_seconds = 20  # 通常の待機
long_wait_timeout_seconds = 30  # JSによる描画など、長めの待機

try:
    driver.get(target_url)

    user_id = input("ユーザーIDを入力してください: ")
    password = getpass.getpass("パスワードを入力してください: ")

    # --- ログイン処理 ---
    username_field = WebDriverWait(driver, wait_timeout_seconds).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username_field.send_keys(user_id)
    # print("Username entered.") # この行はコメントアウト
    sleep(0.2)

    password_field = WebDriverWait(driver, wait_timeout_seconds).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    password_field.send_keys(password)
    # print("Password entered.") # この行はコメントアウト
    sleep(0.2)

    login_button = WebDriverWait(driver, wait_timeout_seconds).until(
        EC.element_to_be_clickable((By.ID, "LoginBtn"))
    )
    login_button.click()
    # print("Login button clicked.") # この行はコメントアウト
    # print("ログイン処理を実行しました。") # この行はコメントアウト

    WebDriverWait(driver, wait_timeout_seconds).until(
        EC.presence_of_element_located((By.XPATH, "//a[contains(@href, 'logout')]"))
    )
    # print(f"Successfully logged in. Current URL: {driver.current_url}") # この行はコメントアウト

    final_all_course_data = []

    # --- ダッシュボードの課題情報を取得 ---
    try:
        # print("Navigating to Dashboard to get course assignments...") # この行はコメントアウト
        dashboard_link_href = "/webclass/ip_mods.php/plugin/score_summary_table/dashboard"
        dashboard_link_locator = (By.XPATH, f"//a[@href='{dashboard_link_href}']")
        
        WebDriverWait(driver, wait_timeout_seconds).until(
            EC.element_to_be_clickable(dashboard_link_locator)
        ).click()
        # print("Dashboard link clicked.") # この行はコメントアウト

        iframe_switched_dashboard = False
        try:
            iframe_locator_dashboard = (By.ID, "ip-iframe")
            WebDriverWait(driver, wait_timeout_seconds).until(
                EC.frame_to_be_available_and_switch_to_it(iframe_locator_dashboard)
            )
            # print("Successfully switched to dashboard iframe (ID='ip-iframe').") # この行はコメントアウト
            iframe_switched_dashboard = True
        except TimeoutException:
            # print("Could not switch to dashboard iframe (ID='ip-iframe'). Assignment data cannot be retrieved.") # この行はコメントアウト
            if driver: driver.save_screenshot("dashboard_iframe_error.png")
        
        if iframe_switched_dashboard:
            course_wrapper_elements_selenium = []
            try:
                WebDriverWait(driver, wait_timeout_seconds).until(
                    EC.presence_of_element_located((By.ID, "app"))
                )
                # print("Dashboard <div id='app'> is present.") # この行はコメントアウト
                # 最初のコースタイトルが表示されるまで待つ
                WebDriverWait(driver, wait_timeout_seconds).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div#app main section.mt-5 section.mt-2 div.mt-2 div[data-v-0e556e9d] a.font-semibold"))
                )
                # print("Initial course title elements presumed loaded.") # この行はコメントアウト
                sleep(2.0)  # JSレンダリングのための追加待機

                # --- Selenium を使ってコースラッパー要素のリストを取得 ---
                app_div_selenium = driver.find_element(By.ID, "app")
                main_element_selenium = app_div_selenium.find_element(By.CSS_SELECTOR, "main.mx-5.mb-10[role='main']")
                
                # main の直接の子 section.mt-5 (学部グループ)
                faculty_sections_selenium = main_element_selenium.find_elements(By.CSS_SELECTOR, ":scope > section.mt-5")
                if not faculty_sections_selenium:  # main の直接の子が学科グループの場合も考慮
                    if main_element_selenium.find_elements(By.CSS_SELECTOR, ":scope > section.mt-2"):
                        # print("[INFO] No 'section.mt-5' found directly under main. Assuming department sections are direct children.") # この行はコメントアウト
                        faculty_sections_selenium = [main_element_selenium]  # main自体を検索対象のルートとする
                    else:
                        pass # print("[WARN] No 'section.mt-5' or 'section.mt-2' found directly under main. Course wrapper search might fail.") # この行はコメントアウト


                for fac_sec_selenium in faculty_sections_selenium:
                    # faculty_section の直接の子 section.mt-2 (学科グループ)
                    department_sections_selenium = fac_sec_selenium.find_elements(By.CSS_SELECTOR, ":scope > section.mt-2")
                    if not department_sections_selenium:  # 学科グループなしで直接コースラッパーがある場合
                        if fac_sec_selenium.find_elements(By.CSS_SELECTOR, f":scope > div.mt-2"):
                            # print(f"  [INFO] No department <section.mt-2> in faculty section. Checking for direct div.mt-2 wrappers.") # この行はコメントアウト
                            department_sections_selenium = [fac_sec_selenium] 

                    for dept_sec_selenium in department_sections_selenium:
                        # department_section の直接の子 div.mt-2 (コースラッパー)
                        wrappers = dept_sec_selenium.find_elements(By.CSS_SELECTOR, f":scope > div.mt-2")
                        for wrapper_sel_candidate in wrappers:
                            try:
                                title_block_sel = wrapper_sel_candidate.find_element(By.CSS_SELECTOR, f":scope > div[data-v-0e556e9d][class*='bg-blue-100']")
                                title_link_sel = title_block_sel.find_element(By.CSS_SELECTOR, "a.font-semibold[href*='/login']")
                                if title_link_sel.text: 
                                    course_wrapper_elements_selenium.append(wrapper_sel_candidate)
                            except NoSuchElementException:
                                # print(f"    [DEBUG] Candidate div.mt-2 is not a valid course wrapper (no title link): {str(wrapper_sel_candidate.get_attribute('outerHTML'))[:150]}")
                                pass 
                    
                # print(f"Found {len(course_wrapper_elements_selenium)} course wrapper WebElements using Selenium.") # この行はコメントアウト

            except TimeoutException:
                # print("[ERROR] Timed out waiting for initial content in iframe <div id='app'> for Selenium search. Cannot proceed.") # この行はコメントアウト
                driver.switch_to.default_content()
                raise 
            except Exception as e_sel_find_wrappers:
                # print(f"[ERROR] Could not find course wrappers using Selenium: {e_sel_find_wrappers}") # この行はコメントアウト
                traceback.print_exc()


            for wrapper_idx, wrapper_element_selenium in enumerate(course_wrapper_elements_selenium):
                course_name = f"不明なコース {wrapper_idx+1}"  # デフォルト名
                course_url = None
                current_course_assignments = []
                assignment_table = None

                try:
                    # --- WebElement から初期HTMLを取得し、コース名とURLを抽出 ---
                    initial_wrapper_html = wrapper_element_selenium.get_attribute("outerHTML")
                    initial_wrapper_soup_node = BeautifulSoup(initial_wrapper_html, "html.parser")
                    # print(f"\n[DEBUG wrapper {wrapper_idx+1}/{len(course_wrapper_elements_selenium)}] Initial wrapper HTML: {initial_wrapper_html[:500]}")

                    title_block_div = initial_wrapper_soup_node.find("div", attrs={"data-v-0e556e9d": True, "class": "relative bg-blue-100 rounded-sm p-2"})
                    course_name_tag = None
                    if title_block_div:
                        course_name_tag = title_block_div.find(
                            "a",
                            attrs={"data-v-0e556e9d": True, "class": "text-base font-semibold text-link hover:text-link-hover"},
                            href=re.compile(r"/webclass/course.php/(?!.*/Info$)")
                        )
                    
                    if course_name_tag:
                        course_name = course_name_tag.get_text(strip=True)
                        course_href = course_name_tag.get('href', '')
                        course_url = urljoin(base_domain, course_href)
                        # print(f"\n[COURSE {wrapper_idx+1}] Processing: {course_name} (URL: {course_url})") # この行はコメントアウト
                    else:
                        h3_title = initial_wrapper_soup_node.find("h3") 
                        course_name_detail = h3_title.get_text(strip=True) if h3_title else 'タイトル特定できず'
                        course_name = f"コース名不明 {wrapper_idx+1} ({course_name_detail})"
                        # print(f"[WARN] {course_name}. Skipping further processing for this wrapper.") # この行はコメントアウト
                        final_all_course_data.append({"course_name": course_name, "course_url": None, "assignments": "コース名リンク特定失敗"})
                        continue
                except Exception as e_get_name:
                    # print(f"  [ERROR] extracting course name from wrapper {wrapper_idx+1}: {e_get_name}") # この行はコメントアウト
                    final_all_course_data.append({"course_name": f"コース名処理エラー {wrapper_idx+1}", "course_url": None, "assignments": "コース名処理エラー"})
                    continue

                # --- テーブル/メッセージコンテナのWebElementを探し、JSによる描画を待機し、最新HTMLを取得 ---
                latest_table_msg_block_soup = None
                try:
                    table_or_msg_container_selenium = wrapper_element_selenium.find_element(By.CSS_SELECTOR, ":scope > div[data-v-8c172e70]")
                    # container_class_name_debug = table_or_msg_container_selenium.get_attribute("class") # この行はコメントアウト
                    # print(f"  [INFO] Found table/message container WebElement for {course_name}. Class: {container_class_name_debug}. Waiting for content...") # この行はコメントアウト

                    # このコンテナ内でローディングアイコンが消えるのを待つ
                    try:
                        WebDriverWait(table_or_msg_container_selenium, long_wait_timeout_seconds).until_not(
                            EC.presence_of_element_located((By.CSS_SELECTOR, "table[data-v-8c172e70] span.loading-icon"))
                        )
                        # print(f"    [INFO] Loading icon within container (if any) disappeared or was not present for {course_name}.") # この行はコメントアウト
                    except TimeoutException:
                        pass # print(f"    [INFO] Timed out waiting for loading icon to disappear for {course_name} (might be no icon initially, or content loaded fast).") # この行はコメントアウト

                    sleep(0.75)  # 安定化のための短い待機
                    
                    latest_table_msg_html_str = table_or_msg_container_selenium.get_attribute("outerHTML")
                    latest_table_msg_block_soup = BeautifulSoup(latest_table_msg_html_str, "html.parser")
                    # print(f"    [INFO] Successfully got latest HTML for table/message container for {course_name}.") # この行はコメントアウト

                except NoSuchElementException:
                    pass # print(f"  [INFO] No div[data-v-8c172e70] (table/message container WebElement) found as direct child of wrapper for {course_name}.") # この行はコメントアウト
                except TimeoutException:  # ローディング待機中のタイムアウトもキャッチ
                    pass # print(f"    [WARN] Timed out waiting for table content to stabilize (e.g. loading icon) for {course_name}.") # この行はコメントアウト
                    # タイムアウトした場合、初期HTMLのコンテナで解析を試みるか、エラーとする
                    # (今回は、latest_table_msg_block_soup が None のままになる)
                except Exception as e_wait_parse:
                    # print(f"  [ERROR] during waiting or parsing latest HTML for {course_name}: {e_wait_parse}") # この行はコメントアウト
                    pass


                if latest_table_msg_block_soup:
                    # BeautifulSoupオブジェクトのルート要素のクラス属性を正しく取得
                    current_block_classes = latest_table_msg_block_soup.find().get("class", []) if latest_table_msg_block_soup.find() else []
                    current_block_text = latest_table_msg_block_soup.get_text(strip=True)
                    
                    # Debugging: Print the classes and a snippet of the text for examination
                    # print(f"  [DEBUG] Block for {course_name} (after wait) classes: {current_block_classes}") # この行はコメントアウト
                    # print(f"  [DEBUG] Block for {course_name} (after wait) text snippet: '{current_block_text[:100]}...'") # この行はコメントアウト

                    # テーブルの探索
                    table_in_block = latest_table_msg_block_soup.find("table", attrs={"data-v-8c172e70": True})
                    if not table_in_block:
                        table_in_block = latest_table_msg_block_soup.find("table", class_=lambda x: x and "table-fixed" in x)  # より一般的なテーブルクラス

                    if table_in_block:
                        # print(f"  [INFO] Block for {course_name} is a TABLE CONTAINER (after wait).") # この行はコメントアウト
                        assignment_table = table_in_block
                    # 「登録されている教材がありません」メッセージの判定を強化
                    elif "登録されている教材がありません" in current_block_text:
                        current_course_assignments = "登録されている教材がありません"
                        # print(f"  [INFO] '登録されている教材がありません' message confirmed for {course_name} (after wait).") # この行はコメントアウト
                    else:
                        pass # print(f"  [INFO] div[data-v-8c172e70] for {course_name} (after wait) is NOT a recognized table container or message. Class: {current_block_classes}, Text: '{current_block_text[:100]}...'") # この行はコメントアウト
                
                if assignment_table:
                    # print(f"  Found assignment table (after wait) for {course_name}") # この行はコメントアウト
                    headers = []
                    thead = assignment_table.find("thead")
                    if thead:
                        header_tags = thead.find_all("th")
                        for th_tag in header_tags:
                            a_tag_in_th = th_tag.find("a")
                            headers.append(a_tag_in_th.get_text(strip=True) if a_tag_in_th else th_tag.get_text(strip=True))
                    if not headers:
                        headers = ["教材", "締切", "実施日", "最高点", "状態"]
                        # print(f"    [WARN] Could not parse headers for {course_name}, using default: {headers}") # この行はコメントアウト
                    else:
                        pass # print(f"    Table Headers: {headers}") # この行はコメントアウト

                    tbody = assignment_table.find("tbody")
                    if tbody:
                        data_rows = [tr for tr in tbody.find_all("tr") if not tr.find("span", class_="loading-icon")]
                        # print(f"    Found {len(data_rows)} actual data rows in tbody for {course_name}.") # この行はコメントアウト
                        for row_idx_tr, row in enumerate(data_rows):
                            cols = row.find_all("td")
                            if not cols or len(cols) < len(headers):
                                if cols: pass # print(f"      [WARN] Row {row_idx_tr+1} for {course_name}: Column count ({len(cols)}) mismatch with headers ({len(headers)}). Skipping.") # この行はコメントアウト
                                continue
                            row_data = {}
                            is_valid_assignment_row = False
                            for i_col, col_el in enumerate(cols):
                                if i_col < len(headers):
                                    header_name = headers[i_col]
                                    span_in_col = col_el.find("span")
                                    cell_text = span_in_col.get_text(strip=True) if span_in_col else col_el.get_text(strip=True)
                                    row_data[header_name] = cell_text
                                    if header_name == "教材" and cell_text:
                                        is_valid_assignment_row = True
                                        material_link_tag_in_cell = col_el.find("a", href=True) or (span_in_col.find("a", href=True) if span_in_col else None)
                                        if material_link_tag_in_cell and material_link_tag_in_cell.get('href') and material_link_tag_in_cell.get('href') != "#":
                                            row_data["教材URL"] = urljoin(driver.current_url, material_link_tag_in_cell['href'])
                                        else:
                                            row_data["教材URL"] = None
                            if is_valid_assignment_row:
                                current_course_assignments.append(row_data)
                            elif any(row_data.values()):
                                pass # print(f"      [INFO] Row {row_idx_tr+1} for {course_name} has non-empty cells but '教材' is missing or empty: {row_data}") # この行はコメントアウト
                    else:
                        pass # print(f"    [WARN] No tbody found in table for {course_name}.") # この行はコメントアウト
                
                elif not current_course_assignments: 
                    current_course_assignments = "課題テーブル/メッセージが見つかりませんでした"
                    # print(f"  [INFO] No assignment table or specific message for {course_name} after all checks.") # この行はコメントアウト

                final_all_course_data.append({
                    "course_name": course_name,
                    "course_url": course_url,
                    "assignments": current_course_assignments
                })
            
            driver.switch_to.default_content()
            # print("Switched back to default content from dashboard iframe.") # この行はコメントアウト
        else:
            pass # print("Skipping assignment extraction as dashboard iframe was not accessible.") # この行はコメントアウト

    except Exception as e_dashboard_processing:
        # print(f"An error occurred while processing the dashboard: {e_dashboard_processing}") # この行はコメントアウト
        traceback.print_exc()
        try:
            driver.switch_to.default_content()
        except:
            pass

    # --- 全てのスクレイピングデータを出力 ---
    if final_all_course_data:
        print("\n\n--- All Scraped Assignment Data ---")
        for item in final_all_course_data:
            print(f"\nCourse: {item['course_name']} (URL: {item.get('course_url', 'N/A')})")
            assignments_data = item['assignments']
            if isinstance(assignments_data, list):
                if assignments_data:
                    for assign_idx, assign_data in enumerate(assignments_data):
                        print(f"  Assignment {assign_idx + 1}:")
                        for key, value in assign_data.items():
                            print(f"    {key}: {value}")
                else:
                    print("  - 課題情報なし (空のリスト).")
            else: 
                print(f"  - {assignments_data}")
        print("---------------------------------\n")
    else:
        print("No assignment data was ultimately scraped from the dashboard.")

except TimeoutException:
    # print("A main timeout occurred (e.g., during login or initial page navigation).") # この行はコメントアウト
    if driver: driver.save_screenshot("main_timeout_error.png")
    # print(f"Current URL on main timeout: {driver.current_url if driver else 'N/A'}") # この行はコメントアウト
    # if driver: print("Page source on main timeout (first 1000 chars):", driver.page_source[:1000]) # この行はコメントアウト
except Exception as e_main_script:
    # print(f"An critical error occurred in the main script: {e_main_script}") # この行はコメントアウト
    traceback.print_exc()
    if driver: driver.save_screenshot("main_script_error.png")

finally:
    # print("処理を終了し、Web Driverを閉じます。") # この行はコメントアウト
    if 'driver' in locals() and driver is not None:
        driver.quit()