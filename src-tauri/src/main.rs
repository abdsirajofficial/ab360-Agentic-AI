// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{CustomMenuItem, Manager, SystemTray, SystemTrayEvent, SystemTrayMenu};
use std::process::{Child, Command};
use std::sync::Mutex;

// Store backend process
struct BackendProcess(Mutex<Option<Child>>);

fn main() {
    // Create system tray
    let quit = CustomMenuItem::new("quit".to_string(), "Quit");
    let hide = CustomMenuItem::new("hide".to_string(), "Hide");
    let show = CustomMenuItem::new("show".to_string(), "Show");
    let tray_menu = SystemTrayMenu::new()
        .add_item(show)
        .add_item(hide)
        .add_item(quit);

    let system_tray = SystemTray::new().with_menu(tray_menu);

    tauri::Builder::default()
        .setup(|app| {
            // Start Python backend
            let backend_process = start_backend(app.handle());
            app.manage(BackendProcess(Mutex::new(backend_process)));
            
            Ok(())
        })
        .system_tray(system_tray)
        .on_system_tray_event(|app, event| match event {
            SystemTrayEvent::LeftClick {
                position: _,
                size: _,
                ..
            } => {
                let window = app.get_window("main").unwrap();
                window.show().unwrap();
                window.set_focus().unwrap();
            }
            SystemTrayEvent::MenuItemClick { id, .. } => match id.as_str() {
                "quit" => {
                    // Kill backend before quitting
                    let state = app.state::<BackendProcess>();
                    if let Some(mut child) = state.0.lock().unwrap().take() {
                        let _ = child.kill();
                    }
                    std::process::exit(0);
                }
                "hide" => {
                    let window = app.get_window("main").unwrap();
                    window.hide().unwrap();
                }
                "show" => {
                    let window = app.get_window("main").unwrap();
                    window.show().unwrap();
                }
                _ => {}
            },
            _ => {}
        })
        .on_window_event(|event| match event.event() {
            tauri::WindowEvent::CloseRequested { api, .. } => {
                event.window().hide().unwrap();
                api.prevent_close();
            }
            _ => {}
        })
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
        use tauri::api::path::resource_dir;
        
        let package_info = app_handle.package_info();
        let resource_path = resource_dir(package_info, &app_handle.env())
            .expect("failed to resolve resource directory");
        
        let backend_path = resource_path.join("ab360-backend.exe");
        
        println!("🚀 Starting backend from: {:?}", backend_path);

        match Command::new(backend_path)
            .spawn() {
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
