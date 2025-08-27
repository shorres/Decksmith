export abstract class BaseComponent {
  protected element: HTMLElement;
  protected isInitialized = false;

  constructor(protected selector: string) {
    const element = document.querySelector(selector);
    if (!element) {
      throw new Error(`Element with selector "${selector}" not found`);
    }
    this.element = element as HTMLElement;
  }

  abstract render(): void;
  abstract initialize(): void;

  protected createElementFromHTML(htmlString: string): HTMLElement {
    const div = document.createElement('div');
    div.innerHTML = htmlString.trim();
    return div.firstChild as HTMLElement;
  }

  protected bindEvent(selector: string, event: string, handler: (e: Event) => void): void {
    const element = this.element.querySelector(selector);
    if (element) {
      element.addEventListener(event, handler);
    }
  }

  show(): void {
    this.element.classList.remove('hidden');
    this.element.classList.add('active');
  }

  hide(): void {
    this.element.classList.remove('active');
    this.element.classList.add('hidden');
  }

  destroy(): void {
    // Override in subclasses if cleanup is needed
  }
}
