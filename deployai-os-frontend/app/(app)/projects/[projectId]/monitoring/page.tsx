import { PageHeader } from "@/components/ui/page-header";
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card";
import { SimpleLineChart } from "@/components/charts/simple-line-chart";
import { SimpleBarChart } from "@/components/charts/simple-bar-chart";
import { monitoringSeries } from "@/lib/mock-data";

export default function MonitoringPage() {
  return (
    <div>
      <PageHeader title="Monitoring" description="Live performance and cost signals for this deployment" />
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Response Latency</CardTitle>
            <CardDescription>Average end-to-end response time (ms), last 24 hours</CardDescription>
          </CardHeader>
          <CardContent>
            <SimpleLineChart data={monitoringSeries.latency} xKey="time" yKey="ms" />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Error Rate</CardTitle>
            <CardDescription>Percentage of requests resulting in an error, last 24 hours</CardDescription>
          </CardHeader>
          <CardContent>
            <SimpleLineChart data={monitoringSeries.errorRate} xKey="time" yKey="pct" color="#dc2626" />
          </CardContent>
        </Card>
      </div>

      <Card className="mt-4">
        <CardHeader>
          <CardTitle>Token Cost</CardTitle>
          <CardDescription>Estimated daily model spend (USD), last 7 days</CardDescription>
        </CardHeader>
        <CardContent>
          <SimpleBarChart data={monitoringSeries.tokenCost} xKey="day" yKey="cost" />
        </CardContent>
      </Card>
    </div>
  );
}
