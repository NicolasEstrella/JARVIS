// System Tray para Jarvis
use tauri::{
    menu::{Menu, MenuItem},
    tray::{MouseButton, MouseButtonState, TrayIconBuilder, TrayIconEvent},
    AppHandle, Emitter, Manager, Runtime,
};

pub fn create_tray<R: Runtime>(app: &AppHandle<R>) -> tauri::Result<()> {
    // Cria itens do menu
    let start_item = MenuItem::with_id(app, "start", "Iniciar Jarvis", true, None::<&str>)?;
    let stop_item = MenuItem::with_id(app, "stop", "Parar Jarvis", true, None::<&str>)?;
    let separator1 = tauri::menu::PredefinedMenuItem::separator(app)?;
    let panel_item = MenuItem::with_id(app, "panel", "Abrir Painel", true, None::<&str>)?;
    let separator2 = tauri::menu::PredefinedMenuItem::separator(app)?;
    let quit_item = MenuItem::with_id(app, "quit", "Sair", true, None::<&str>)?;

    // Cria menu do tray
    let menu = Menu::with_items(
        app,
        &[
            &start_item,
            &stop_item,
            &separator1,
            &panel_item,
            &separator2,
            &quit_item,
        ],
    )?;

    // Cria ícone do tray
    let _tray = TrayIconBuilder::new()
        .menu(&menu)
        .icon(app.default_window_icon().unwrap().clone())
        .tooltip("Jarvis Assistant")
        .on_menu_event(move |app, event| {
            match event.id.as_ref() {
                "start" => {
                    println!("  Menu: Iniciar Jarvis");
                    // Chama comando para iniciar Jarvis
                    let _ = app.emit("jarvis-start", ());
                }
                "stop" => {
                    println!("  Menu: Parar Jarvis");
                    // Chama comando para parar Jarvis
                    let _ = app.emit("jarvis-stop", ());
                }
                "panel" => {
                    println!("📱 Menu: Abrir Painel");
                    // Mostra janela principal
                    if let Some(window) = app.get_webview_window("main") {
                        let _ = window.show();
                        let _ = window.set_focus();
                    }
                }
                "quit" => {
                    println!("👋 Menu: Sair");
                    // Para Jarvis antes de sair
                    let _ = app.emit("jarvis-stop", ());
                    std::process::exit(0);
                }
                _ => {}
            }
        })
        .on_tray_icon_event(|tray, event| {
            // Duplo clique abre painel
            if let TrayIconEvent::Click {
                button: MouseButton::Left,
                button_state: MouseButtonState::Up,
                ..
            } = event
            {
                let app = tray.app_handle();
                if let Some(window) = app.get_webview_window("main") {
                    let _ = window.show();
                    let _ = window.set_focus();
                }
            }
        })
        .build(app)?;

    Ok(())
}
