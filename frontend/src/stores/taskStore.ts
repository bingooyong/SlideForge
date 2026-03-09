import { create } from "zustand";

export type TaskStatusEnum = "queued" | "processing" | "completed" | "failed";

export type TaskStageEnum = "uploading" | "processing" | "synthesizing" | "completed";

export interface TaskStatus {
  taskId: string;
  filename?: string;
  status: TaskStatusEnum;
  progress: number;
  currentPage: number;
  totalPages: number;
  stage: TaskStageEnum;
  failedPages: number[];
}

interface TaskStoreState {
  tasks: Record<string, TaskStatus>;
  upsertTask: (task: TaskStatus) => void;
  updateTask: (taskId: string, partial: Partial<TaskStatus>) => void;
  reset: () => void;
}

export const useTaskStore = create<TaskStoreState>((set) => ({
  tasks: {},
  upsertTask: (task) =>
    set((state) => ({
      tasks: {
        ...state.tasks,
        [task.taskId]: task,
      },
    })),
  updateTask: (taskId, partial) =>
    set((state) => {
      const existing = state.tasks[taskId];
      if (!existing) {
        return state;
      }
      return {
        tasks: {
          ...state.tasks,
          [taskId]: {
            ...existing,
            ...partial,
          },
        },
      };
    }),
  reset: () => set({ tasks: {} }),
}));

