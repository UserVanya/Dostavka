import General
import datetime
if __name__ == "__main__":
    General.save_delivery_excel(
        date=datetime.date(2024, 12, 13),
        collector_salary=800,
        drivers_salary=7580,
        additional_costs=1422,
        deliveries_total=43,
        deliveries_internal=9,
        deliveries_distance=367
    )