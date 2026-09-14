from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.utils import platform

# Если мы запускаем на Android, подключаем системный WebView через PyJNIus
if platform == 'android':
    from jnius import autoclass
    from android.runnable import run_on_ui_thread

    Activity = autoclass('org.kivy.android.PythonActivity').mActivity
    WebView = autoclass('android.webkit.WebView')
    WebViewClient = autoclass('android.webkit.WebViewClient')
else:
    # Заглушка, чтобы код запускался и на компьютере при тестах
    def run_on_ui_thread(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper

class BrowserLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(BrowserLayout, self).__init__(**kwargs)
        self.orientation = 'vertical'
        
        # Создаем верхнюю панель навигации
        self.nav_bar = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        
        # Поле ввода URL-адреса
        self.url_input = TextInput(text='https://www.google.com', multiline=False)
        self.nav_bar.add_widget(self.url_input)
        
        # Кнопка перехода
        self.go_button = Button(text='Go', size_hint_x=0.2)
        self.go_button.bind(on_press=self.load_url_from_input)
        self.nav_bar.add_widget(self.go_button)
        
        self.add_widget(self.nav_bar)
        
        # Выделяем место под WebView (занимает оставшиеся 90% экрана)
        self.browser_space = BoxLayout(size_hint_y=0.9)
        self.add_widget(self.browser_space)
        
        self.webview = None
        # Инициализируем браузер после загрузки интерфейса
        self.init_webview()

    @run_on_ui_thread
    def init_webview(self):
        if platform == 'android':
            self.webview = WebView(Activity)
            self.webview.getSettings().setJavaScriptEnabled(True) # Включаем JavaScript
            self.webview.setWebViewClient(WebViewClient())
            
            # Добавляем нативный Android-виджет внутрь Kivy-приложения
            Activity.addContentView(self.webview, autoclass('android.view.ViewGroup$LayoutParams')(-1, -1))
            self.webview.loadUrl(self.url_input.text)

    def load_url_from_input(self, instance):
        url = self.url_input.text
        if not url.startswith('http://') and not url.startswith('https://'):
            url = 'https://' + url
            self.url_input.text = url
        self.open_url(url)

    @run_on_ui_thread
    def open_url(self, url):
        if self.webview:
            self.webview.loadUrl(url)
        else:
            print(f"Открытие URL (не на Android): {url}")

class SimpleBrowserApp(App):
    def build(self):
        return BrowserLayout()

if __name__ == '__main__':
    SimpleBrowserApp().run()

