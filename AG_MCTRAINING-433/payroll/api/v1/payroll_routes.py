from fastapi import APIRouter, Depends, HTTPException

from payroll.core.dependencies import get_payroll_service
from payroll.models.payroll import PayrollCreateRequest, PayrollUpdateRequest
from payroll.services.payroll_service import PayrollService

router = APIRouter(tags=["payroll"])


@router.get("/payroll/")
async def list_all_payrolls(
    service: PayrollService = Depends(get_payroll_service),
):
    return service.list_all_payrolls()


@router.post("/payroll/", status_code=201)
async def create_payroll(
    body: PayrollCreateRequest,
    service: PayrollService = Depends(get_payroll_service),
):
    payroll_id = service.create_payroll(body.model_dump())
    return {"message": "Payroll record created", "payrollId": payroll_id}


@router.get("/payroll/user/{user_id}")
async def list_payroll_by_user(
    user_id: str,
    service: PayrollService = Depends(get_payroll_service),
):
    records = service.list_payroll_by_user(user_id)
    return {"userId": user_id, "records": records}


@router.get("/payroll/{payroll_id}")
async def get_payroll(
    payroll_id: str,
    service: PayrollService = Depends(get_payroll_service),
):
    record = service.get_payroll(payroll_id)
    if not record:
        raise HTTPException(status_code=404, detail="Payroll record not found")
    return record


@router.put("/payroll/{payroll_id}")
async def update_payroll(
    payroll_id: str,
    body: PayrollUpdateRequest,
    service: PayrollService = Depends(get_payroll_service),
):
    updated = service.update_payroll(payroll_id, body.model_dump(exclude_none=True))
    if not updated:
        raise HTTPException(status_code=404, detail="Payroll record not found")
    return {"message": "Payroll record updated"}


@router.delete("/payroll/{payroll_id}", status_code=200)
async def delete_payroll(
    payroll_id: str,
    service: PayrollService = Depends(get_payroll_service),
):
    service.delete_payroll(payroll_id)
    return {"message": "Payroll record deleted"}
