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

  // Public getter to check initialization status
  get initialized(): boolean {
    return this.isInitialized;
  }

  abstract render(): void;
  abstract initialize(): void;

  protected bindEvent(selector: string, event: string, handler: (e: Event) => void): void {
    const element = this.element.querySelector(selector);
    if (element) {
      element.addEventListener(event, (e) => {
        try {
          handler(e);
        } catch (error) {
          console.error(`Error in ${event} handler for ${selector}:`, error);
        }
      });
    } else {
      console.warn(`Element not found for selector: ${selector}`);
    }
  }
}
