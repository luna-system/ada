import { writable } from 'svelte/store';

export type Panel = 'none' | 'debug' | 'mem' | 'prompt' | 'conversations';

export const panelOpen = writable<Panel>('none');
export const menuOpen = writable<boolean>(false);
