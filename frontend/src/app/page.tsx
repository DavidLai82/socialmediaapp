import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Bot, TrendingUp, VideoIcon, MessageSquare, BarChart } from 'lucide-react'

export default function Home() {
  return (
    <main className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">
          Social Media AI Platform
        </h1>
        <p className="text-xl text-muted-foreground mb-6">
          Multi-agent AI platform for social media optimization
        </p>
        <div className="flex justify-center gap-4">
          <Button size="lg">
            Get Started
          </Button>
          <Button variant="outline" size="lg">
            Learn More
          </Button>
        </div>
      </div>

      {/* Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-12">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Active Agents
            </CardTitle>
            <Bot className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">5</div>
            <p className="text-xs text-muted-foreground">
              All systems operational
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Active Tasks
            </CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">
              +4 from last hour
            </p>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">
              Content Generated
            </CardTitle>
            <MessageSquare className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">47</div>
            <p className="text-xs text-muted-foreground">
              Today's total
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
        <Card>
          <CardHeader>
            <div className="flex items-center space-x-2">
              <Bot className="h-5 w-5" />
              <CardTitle className="text-lg">Social Optimizer</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <CardDescription>
              Main coordinator agent that manages all social media optimization activities
            </CardDescription>
            <Badge className="mt-2" variant="secondary">Active</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center space-x-2">
              <BarChart className="h-5 w-5" />
              <CardTitle className="text-lg">Traffic Analyst</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <CardDescription>
              Analyzes trends and predicts viral content opportunities across platforms
            </CardDescription>
            <Badge className="mt-2" variant="secondary">Active</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center space-x-2">
              <MessageSquare className="h-5 w-5" />
              <CardTitle className="text-lg">Content Writer</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <CardDescription>
              Creates engaging, platform-optimized content with brand voice consistency
            </CardDescription>
            <Badge className="mt-2" variant="secondary">Active</Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center space-x-2">
              <VideoIcon className="h-5 w-5" />
              <CardTitle className="text-lg">Video Creator</CardTitle>
            </div>
          </CardHeader>
          <CardContent>
            <CardDescription>
              Plans video content with comprehensive scripts and production guidelines
            </CardDescription>
            <Badge className="mt-2" variant="secondary">Active</Badge>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Start generating content with our AI agents
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
              <MessageSquare className="h-6 w-6 mb-2" />
              Generate Content
            </Button>
            <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
              <BarChart className="h-6 w-6 mb-2" />
              Analyze Trends
            </Button>
            <Button variant="outline" className="h-20 flex flex-col items-center justify-center">
              <VideoIcon className="h-6 w-6 mb-2" />
              Create Video Plan
            </Button>
          </div>
        </CardContent>
      </Card>
    </main>
  )
}