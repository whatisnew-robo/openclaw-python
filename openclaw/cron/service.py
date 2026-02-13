"""
Cron job scheduling service - 完整的AI驱动智能定时任务系统

提供与TypeScript版本完全对齐的定时任务功能：
- 三种调度类型（at/every/cron）
- 隔离Agent执行（智能任务）  
- 系统事件（简单通知）
- 持久化存储
- 运行日志
- 自动交付
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Dict, Callable, Awaitable, Union

from .types import (
    CronJob,
    AgentTurnPayload,
    SystemEventPayload,
    CronJobState
)
from .schedule import compute_next_run
from .timer import CronTimer
from .store import CronStore, CronRunLog

logger = logging.getLogger(__name__)


class CronService:
    """
    完整的Cron调度服务
    
    功能：
    - 三种调度类型（at/every/cron）
    - 隔离Agent执行（智能任务）
    - 系统事件（简单通知）
    - 持久化存储
    - 运行日志
    - 自动交付
    """
    
    def __init__(
        self,
        store_path: Optional[Path] = None,
        log_dir: Optional[Path] = None,
        on_system_event: Optional[Callable[[str, Optional[str]], Awaitable[None]]] = None,
        on_isolated_agent: Optional[Callable[[CronJob], Awaitable[Dict[str, Any]]]] = None,
        on_event: Optional[Callable[[Dict[str, Any]], None]] = None,
    ):
        """
        初始化Cron服务
        
        Args:
            store_path: Job存储路径
            log_dir: 运行日志目录
            on_system_event: 系统事件回调 (text, agent_id)
            on_isolated_agent: 隔离Agent执行回调 (job) -> result
            on_event: 事件广播回调 (event)
        """
        self.jobs: Dict[str, CronJob] = {}
        self._running = False
        
        # 配置
        self.store_path = store_path
        self.log_dir = log_dir
        self.on_system_event = on_system_event
        self.on_isolated_agent = on_isolated_agent
        self.on_event = on_event
        
        # 存储和日志
        self._store: Optional[CronStore] = None
        if store_path:
            self._store = CronStore(store_path)
        
        # 定时器
        self._timer: Optional[CronTimer] = None
        
        logger.info("CronService initialized")
    
    def start(self) -> None:
        """启动Cron服务"""
        if self._running:
            logger.warning("CronService already running")
            return
        
        self._running = True
        
        # 创建并启动定时器
        self._timer = CronTimer(on_timer_callback=self._on_timer_fired)
        self._timer.arm_timer(list(self.jobs.values()))
        
        logger.info(f"✅ CronService started with {len(self.jobs)} jobs")
        self._broadcast_event({
            "action": "service-started",
            "job_count": len(self.jobs),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    
    def stop(self) -> None:
        """停止Cron服务"""
        if not self._running:
            return
        
        self._running = False
        
        if self._timer:
            self._timer.stop()
            self._timer = None
        
        logger.info("CronService stopped")
        self._broadcast_event({
            "action": "service-stopped",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
    
    # 兼容旧API名称
    def shutdown(self) -> None:
        """停止服务（兼容旧API）"""
        self.stop()
    
    def add_job(self, job: CronJob) -> bool:
        """
        添加定时任务
        
        Args:
            job: 任务定义
            
        Returns:
            成功返回True
        """
        try:
            # 计算首次运行时间
            now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
            
            if job.state.next_run_ms is None:
                job.state.next_run_ms = compute_next_run(job.schedule, now_ms)
            
            # 添加到内存
            self.jobs[job.id] = job
            
            # 持久化
            if self._store:
                self._store.save(list(self.jobs.values()))
            
            # 重新调度timer
            if self._timer and self._running:
                self._timer.arm_timer(list(self.jobs.values()))
            
            logger.info(f"✅ Added cron job: {job.name} (id={job.id})")
            self._broadcast_event({
                "action": "job-added",
                "jobId": job.id,
                "jobName": job.name,
                "nextRun": job.state.next_run_ms,
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add job {job.id}: {e}", exc_info=True)
            return False
    
    def update_job(self, job: CronJob) -> bool:
        """
        更新任务
        
        Args:
            job: 更新后的任务定义
            
        Returns:
            成功返回True
        """
        try:
            if job.id not in self.jobs:
                logger.error(f"Job {job.id} not found")
                return False
            
            # 重新计算next_run
            now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
            job.state.next_run_ms = compute_next_run(job.schedule, now_ms)
            
            # 更新
            self.jobs[job.id] = job
            
            # 持久化
            if self._store:
                self._store.save(list(self.jobs.values()))
            
            # 重新调度
            if self._timer and self._running:
                self._timer.arm_timer(list(self.jobs.values()))
            
            logger.info(f"✅ Updated job: {job.id}")
            self._broadcast_event({
                "action": "job-updated",
                "jobId": job.id,
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to update job {job.id}: {e}", exc_info=True)
            return False
    
    def remove_job(self, job_id: str) -> bool:
        """
        删除任务
        
        Args:
            job_id: 任务ID
            
        Returns:
            成功返回True
        """
        try:
            if job_id not in self.jobs:
                logger.error(f"Job {job_id} not found")
                return False
            
            # 删除
            job = self.jobs.pop(job_id)
            
            # 持久化
            if self._store:
                self._store.save(list(self.jobs.values()))
            
            # 重新调度
            if self._timer and self._running:
                self._timer.arm_timer(list(self.jobs.values()))
            
            logger.info(f"✅ Removed job: {job_id}")
            self._broadcast_event({
                "action": "job-removed",
                "jobId": job_id,
            })
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}", exc_info=True)
            return False
    
    def list_jobs(self, include_disabled: bool = False) -> list[Dict[str, Any]]:
        """
        列出所有任务
        
        Args:
            include_disabled: 是否包含禁用的任务
            
        Returns:
            任务列表
        """
        jobs = list(self.jobs.values())
        
        if not include_disabled:
            jobs = [j for j in jobs if j.enabled]
        
        return [self._job_to_dict(job) for job in jobs]
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        获取任务状态
        
        Args:
            job_id: 任务ID
            
        Returns:
            任务状态字典，不存在返回None
        """
        job = self.jobs.get(job_id)
        if not job:
            return None
        
        return self._job_to_dict(job)
    
    # 兼容旧API名称
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status (alias for get_job_status)"""
        return self.get_job_status(job_id)
    
    async def run_job_now(self, job_id: str) -> Dict[str, Any]:
        """
        立即运行任务
        
        Args:
            job_id: 任务ID
            
        Returns:
            执行结果
        """
        job = self.jobs.get(job_id)
        if not job:
            return {
                "success": False,
                "error": f"Job {job_id} not found"
            }
        
        logger.info(f"🚀 Running job immediately: {job.name} (id={job_id})")
        
        result = await self._execute_job(job)
        
        return result
    
    async def _on_timer_fired(self, due_jobs: list[CronJob]) -> None:
        """
        定时器触发 - 执行所有到期任务
        
        Args:
            due_jobs: 到期的任务列表
        """
        logger.info(f"⏰ Timer fired: {len(due_jobs)} due jobs")
        
        for job in due_jobs:
            if not job.enabled:
                continue
            
            try:
                await self._execute_job(job)
            except Exception as e:
                logger.error(f"Error executing job {job.id}: {e}", exc_info=True)
    
    async def _execute_job(self, job: CronJob) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            job: 要执行的任务
            
        Returns:
            执行结果
        """
        if not job.enabled:
            logger.debug(f"Job {job.id} is disabled, skipping")
            return {"success": False, "error": "Job disabled"}
        
        # 更新状态
        now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
        job.state.running_at_ms = now_ms
        
        # 广播开始事件
        self._broadcast_event({
            "action": "job-started",
            "jobId": job.id,
            "jobName": job.name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        })
        
        start_time = datetime.now(timezone.utc)
        result: Dict[str, Any] = {"success": False}
        
        try:
            # 根据payload类型执行
            if isinstance(job.payload, SystemEventPayload):
                result = await self._execute_system_event(job)
            elif isinstance(job.payload, AgentTurnPayload):
                result = await self._execute_agent_turn(job)
            else:
                raise ValueError(f"Unknown payload type: {type(job.payload)}")
            
            # 更新状态
            job.state.last_run_at_ms = now_ms
            job.state.last_status = "success" if result.get("success") else "error"
            job.state.last_error = result.get("error")
            
        except Exception as e:
            logger.error(f"Job {job.id} execution error: {e}", exc_info=True)
            result = {
                "success": False,
                "error": str(e)
            }
            job.state.last_status = "error"
            job.state.last_error = str(e)
        
        finally:
            # 计算耗时
            duration_ms = int((datetime.now(timezone.utc) - start_time).total_seconds() * 1000)
            job.state.last_duration_ms = duration_ms
            job.state.running_at_ms = None
            
            # 计算下次运行时间
            if not job.delete_after_run:
                job.state.next_run_ms = compute_next_run(
                    job.schedule,
                    int(datetime.now(timezone.utc).timestamp() * 1000)
                )
            else:
                # 一次性任务，执行后删除
                logger.info(f"Job {job.id} is one-shot, removing after execution")
                self.remove_job(job.id)
                return result  # 早退出，因为job已删除
            
            # 持久化状态
            if self._store and job.id in self.jobs:
                self._store.save(list(self.jobs.values()))
            
            # 记录运行日志
            if self.log_dir:
                try:
                    run_log = CronRunLog(self.log_dir, job.id)
                    run_log.append({
                        "timestamp": start_time.isoformat(),
                        "duration_ms": duration_ms,
                        "status": job.state.last_status,
                        "error": job.state.last_error,
                        "summary": result.get("summary"),
                    })
                except Exception as e:
                    logger.warning(f"Failed to write run log: {e}")
            
            # 广播完成事件
            self._broadcast_event({
                "action": "job-finished",
                "jobId": job.id,
                "jobName": job.name,
                "status": job.state.last_status,
                "durationMs": duration_ms,
                "error": job.state.last_error,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            })
        
        return result
    
    async def _execute_system_event(self, job: CronJob) -> Dict[str, Any]:
        """
        执行系统事件
        
        Args:
            job: 任务
            
        Returns:
            执行结果
        """
        payload = job.payload
        if not isinstance(payload, SystemEventPayload):
            return {"success": False, "error": "Invalid payload type"}
        
        if not payload.text:
            logger.warning(f"Job {job.id} has empty systemEvent text, skipping")
            return {"success": False, "error": "Empty system event text"}
        
        logger.info(f"📨 Executing systemEvent for job {job.name}")
        
        try:
            if self.on_system_event:
                await self.on_system_event(payload.text, job.agent_id)
                return {
                    "success": True,
                    "summary": payload.text,
                }
            else:
                logger.warning("on_system_event callback not configured")
                return {
                    "success": False,
                    "error": "System event callback not configured"
                }
                
        except Exception as e:
            logger.error(f"System event execution error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _execute_agent_turn(self, job: CronJob) -> Dict[str, Any]:
        """
        执行Agent turn（智能任务）
        
        Args:
            job: 任务
            
        Returns:
            执行结果 {success, summary, full_response, session_key, model, ...}
        """
        payload = job.payload
        if not isinstance(payload, AgentTurnPayload):
            return {"success": False, "error": "Invalid payload type"}
        
        if not payload.prompt:
            logger.warning(f"Job {job.id} has empty agentTurn prompt, skipping")
            return {"success": False, "error": "Empty prompt"}
        
        logger.info(f"🤖 Executing agentTurn for job {job.name}")
        logger.info(f"   Prompt: {payload.prompt[:100]}...")
        
        try:
            if self.on_isolated_agent:
                # 调用隔离Agent执行
                result = await self.on_isolated_agent(job)
                
                logger.info(f"✅ Agent turn completed: {result.get('success')}")
                if result.get("summary"):
                    logger.info(f"   Summary: {result['summary'][:100]}...")
                
                return result
            else:
                logger.error("on_isolated_agent callback not configured")
                return {
                    "success": False,
                    "error": "Isolated agent callback not configured"
                }
                
        except Exception as e:
            logger.error(f"Agent turn execution error: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
    
    def _job_to_dict(self, job: CronJob) -> Dict[str, Any]:
        """转换Job为字典"""
        result = job.to_dict()
        
        # 添加运行时信息
        if job.state.next_run_ms:
            result["nextRun"] = datetime.fromtimestamp(
                job.state.next_run_ms / 1000, 
                tz=timezone.utc
            ).isoformat()
        
        if job.state.last_run_at_ms:
            result["lastRun"] = datetime.fromtimestamp(
                job.state.last_run_at_ms / 1000,
                tz=timezone.utc
            ).isoformat()
        
        result["running"] = job.state.running_at_ms is not None
        
        return result
    
    def _broadcast_event(self, event: Dict[str, Any]) -> None:
        """广播事件"""
        try:
            if self.on_event:
                self.on_event(event)
        except Exception as e:
            logger.error(f"Error broadcasting event: {e}", exc_info=True)


# 全局单例
_cron_service: Optional[CronService] = None


def get_cron_service() -> CronService:
    """获取全局CronService实例"""
    global _cron_service
    if _cron_service is None:
        _cron_service = CronService()
    return _cron_service


def set_cron_service(service: CronService) -> None:
    """设置全局CronService实例"""
    global _cron_service
    _cron_service = service
