from fastapi import APIRouter

from .audit import router as audit_router
from .capa import router as capa_router
from .document import router as document_router
from .equipment import router as equipment_router
from .inspection import router as inspection_router
from .logging import router as logging_router
from .master import router as master_router
from .nonconformance import router as nonconformance_router
from .order import router as order_router
from .process import router as process_router
from .production import router as production_router
from .review import router as review_router
from .training import router as training_router

router = APIRouter(prefix="/api/erp")
router.include_router(audit_router)
router.include_router(capa_router)
router.include_router(document_router)
router.include_router(equipment_router)
router.include_router(inspection_router)
router.include_router(logging_router)
router.include_router(master_router)
router.include_router(nonconformance_router)
router.include_router(order_router)
router.include_router(process_router)
router.include_router(production_router)
router.include_router(review_router)
router.include_router(training_router)
