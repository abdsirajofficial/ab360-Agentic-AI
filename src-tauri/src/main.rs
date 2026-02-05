// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use std::process::{Child, Command};
use std::sync::Mutex;
use tauri::{Manager, State};
use tauri::menu::{Menu, MenuItem};
use tauri::tray::{TrayIconBuilder, TrayIconEvent};

// Store backend process
struct BackendProcess(Mutex<Option<Child>>);

fn main() {
    tauri::Builder::default()
        .setup(|app| {
            // Create system tray menu
            let quit = MenuItem::with_id(app, "quit", "Quit", true, None::<&str>)?;
            let show = MenuItem::with_id(app, "show", "Show", true, None::<&str>)?;
            let hide = MenuItem::with_id(app, "hide", "Hide", true, None::<&str>)?;
            
            let menu = Menu::with_items(app, &[&show, &hide, &quit])?;
            
            // Build tray icon
            let _tray = TrayIconBuilder::new()
                .menu(&menu)
                .on_menu_event(|app, event| match event.id.as_ref() {
                    "quit" => {
                        // Kill backend before quitting
                        let state = app.state::<BackendProcess>();
                        if let Some(mut child) = state.0.lock().unwrap().take() {
                            let _ = child.kill();
                        }
                        app.exit(0);
                    }
                    "hide" => {
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.hide();
                        }
                    }
                    "show" => {
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                    _ => {}
                })
                .on_tray_icon_event(|tray, event| {
                    if let TrayIconEvent::Click { .. } = event {
                        let app = tray.app_handle();
                        if let Some(window) = app.get_webview_window("main") {
                            let _ = window.show();
                            let _ = window.set_focus();
                        }
                    }
                })
                .build(app)?;

            // Start Python backend
            let backend_process = start_backend(app.handle());
            app.manage(BackendProcess(Mutex::new(backend_process)));
            
            Ok(())
        })
        .on_window_event(|window, event| {
            if let tauri::WindowEvent::CloseRequested { api, .. } = event {
                window.hide().unwrap();
                api.prevent_close();
            }
        })
        .plugin(tauri_plugin_shell::init())
        .invoke_handler(tauri::generate_handler![
            toggle_always_on_top,
            show_window,
            hide_window
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

fn start_backend(app_handle: tauri::AppHandle) -> Option<Child> {
    #[cfg(debug_assertions)]
    {
        // In development, don't start backend (assume it's running separately)
        println!("🔧 Development mode: Backend should be running separately on port 8000");
        return None;
    }

    #[cfg(not(debug_assertions))]
    {
        // In production, start bundled backend
        use tauri::Manager;
        
        let resource_path = app_handle
            .path()
            .resource_dir()
            .expect("failed to resolve resource directory");
        
        let backend_path = resource_path.join("ab360-backend.exe");
        
        println!("🚀 Starting backend from: {:?}", backend_path);

        match Command::new(backend_path).spawn() {
            Ok(child) => {
                println!("✅ Backend started with PID: {}", child.id());
                
                // Wait a moment for backend to start
                std::thread::sleep(std::time::Duration::from_secs(2));
                
                Some(child)
            }
            Err(e) => {
                eprintln!("❌ Failed to start backend: {}", e);
                None
            }
        }
    }
}

#[tauri::command]
fn toggle_always_on_top(window: tauri::Window) -> Result<bool, String> {
    let is_on_top = window.is_always_on_top().map_err(|e| e.to_string())?;
    window
        .set_always_on_top(!is_on_top)
        .map_err(|e| e.to_string())?;
    Ok(!is_on_top)
}

#[tauri::command]
fn show_window(window: tauri::Window) -> Result<(), String> {
    window.show().map_err(|e| e.to_string())?;
    window.set_focus().map_err(|e| e.to_string())?;
    Ok(())
}

#[tauri::command]
fn hide_window(window: tauri::Window) -> Result<(), String> {
    window.hide().map_err(|e| e.to_string())?;
    Ok(())
}
