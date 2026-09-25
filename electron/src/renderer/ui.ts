// Shared DOM helpers for the shell modal, status bar and HTML escaping

let modalCleanup: (() => void) | null = null;

// Opens the shared #modal. `onClose` runs once when the modal is closed (e.g. to remove listeners).
export function openModal(title: string, html: string, onClose?: () => void): void {
  const modal = document.getElementById('modal');
  const modalTitle = document.getElementById('modal-title');
  const modalContent = document.getElementById('modal-content');
  if (!modal || !modalTitle || !modalContent) return;

  closeModal();
  modalTitle.textContent = title;
  modalContent.innerHTML = html;
  modalCleanup = onClose ?? null;
  modal.classList.remove('hidden');
}

export function closeModal(): void {
  document.getElementById('modal')?.classList.add('hidden');
  if (modalCleanup) {
    const cleanup = modalCleanup;
    modalCleanup = null;
    cleanup();
  }
}

let statusTimeout = 0;

// Shows a message in the status bar. Transient messages revert to "Ready" after 3 seconds.
export function setStatus(message: string, transient = true): void {
  const statusElement = document.getElementById('status-message');
  if (!statusElement) return;

  statusElement.textContent = message;
  clearTimeout(statusTimeout);
  if (transient) {
    statusTimeout = window.setTimeout(() => {
      statusElement.textContent = 'Ready';
    }, 3000);
  }
}

export function setCardCount(count: number): void {
  const countElement = document.getElementById('card-count');
  if (countElement) {
    countElement.textContent = `${count} cards loaded`;
  }
}

const HTML_ESCAPES: Record<string, string> = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
};

// Escapes text for use in HTML content or a quoted attribute value
export function escapeHtml(value: string | undefined | null): string {
  return (value ?? '').replace(/[&<>"']/g, ch => HTML_ESCAPES[ch]);
}
